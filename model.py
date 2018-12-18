#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from json import load

#logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("model")


class ClientModel(object):
    def __init__(self, definition_file="lwm2m-object-definitions.json", data_file="data.json"):
        with open(definition_file) as f:
            self.definition = load(f)
        with open(data_file) as f:
            self.data = load(f)
        # simple validation: check if all data objects are in the definition
        for obj in self.objects():
            if not self.has_definition(obj):
                exit("%s contains undefined object with ID %s. Aborting." % (data_file, obj))

    def objects(self):
        return [x for x in sorted([int(i) for i in self.data.keys()])]

    def instances(self, obj):
        _insts = self.data[str(obj)]
        return [x for x in sorted([int(i) for i in _insts.keys()])]

    def resources(self, obj, inst=0):
        return [x for x in sorted([int(i) for i in self.data[str(obj)][str(inst)].keys()])]

    def resource(self, obj, inst, res):
        return self.data[str(obj)][str(inst)][str(res)]

    def has_definition(self, obj):
        return str(obj) in self.definition.keys()

    def is_object_multi_instance(self, obj):
        return self.definition[str(obj)]["instancetype"] == "multiple"

    def is_resource_multi_instance(self, obj, inst, res):
        return self.definition[str(obj)]["resourcedefs"][str(res)]["instancetype"] == "multiple"

    def resource_iter(self):
        for obj in self.objects():
            for inst in self.instances(obj):
                for res in self.resources(obj, inst):
                    yield (str(obj), str(inst), str(res))

    def instance_iter(self):
        for obj in self.objects():
            for inst in self.instances(obj):
                yield (str(obj), str(inst))

    def get_object_links(self, all=False):
        for obj in self.objects():
            for inst in self.instances(obj):
                if not all and obj == 0:
                    continue
                yield "</%s/%s>" % (obj, inst)

    def is_path_valid(self, path):
        if len(path) == 3:
            _obj = int(path[0])
            _inst = int(path[1])
            _res = int(path[2])
            return _obj in self.objects() and _inst in self.instances(_obj) and _res in self.resources(_obj, _inst)
        elif len(path) == 2:
            _obj = int(path[0])
            _inst = int(path[1])
            return _obj in self.objects() and _inst in self.instances(_obj)
        elif len(path) == 1:
            _obj = int(path[0])
            return _obj in self.objects()
        else:
            raise AttributeError("invalid path length: %d." % len(path))

    def is_resource_readable(self, obj, inst, res):
        _ops = self.definition[obj]["resourcedefs"][str(res)]["operations"]
        return False if _ops == "NONE" else "R" in _ops

    def is_resource_executable(self, obj, inst, res):
        _ops = self.definition[obj]["resourcedefs"][str(res)]["operations"]
        return False if _ops == "NONE" else "E" in _ops

    def set_resource(self, obj, inst, res, content):
        self.data[str(obj)][str(inst)][str(res)] = content

    def apply(self, data):
        for obj in data.keys():
            for inst in data[obj].keys():
                for res in data[obj][inst].keys():
                    logger.debug("applying %s/%s/%s = %s" % (obj, inst, res, data[obj][inst][res]))
                    self.set_resource(obj, inst, res, data[obj][inst][res])


if __name__ == '__main__':
    model = ClientModel()
    logger.debug("object links: %s" % ",".join(model.get_object_links()))
    logger.debug("objects: %s" % model.objects())
    for obj in model.objects():
        logger.debug("object %s is multi-instance: %s" % (obj, model.is_object_multi_instance(obj)))
        logger.debug("instances for object %s: %s" % (obj, model.instances(obj)))
        for inst in model.instances(obj):
            logger.debug("resources for /%s/%s: %s" % (obj, inst, model.resources(obj, inst)))
            logger.debug("===============================================================================================")
            for res in model.resources(obj, inst):
                logger.debug("resource /%s/%s/%s is multi-instance: %s" % (
                    obj, inst, res, model.is_resource_multi_instance(obj, inst, res)))
                logger.debug("resource /%s/%s/%s: \"%s\"" % (obj, inst, res, model.resource(obj, inst, res)))
            logger.debug("===============================================================================================")
