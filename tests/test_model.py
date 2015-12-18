#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

import pytest

from model import ClientModel, DefinitionFileLoader, DataFileLoader


@pytest.fixture
def empty_data_loader():
    class Loader(object):
        def __init__(self):
            pass

        def load(self):
            return json.loads("{}")

    return Loader()


@pytest.fixture
def empty_definition_loader():
    class Loader(object):
        def __init__(self):
            pass

        def load(self):
            return json.loads("{}")

    return Loader()


@pytest.fixture
def model(definition_loader=DefinitionFileLoader(), data_loader=DataFileLoader()):
    return ClientModel(definition_loader=definition_loader, data_loader=data_loader)


def test_invalid_definition_loader():
    with pytest.raises(AttributeError):
        ClientModel(definition_loader=1)


def test_invalid_data_loader():
    with pytest.raises(AttributeError):
        ClientModel(data_loader=1)


def test_non_existing_definition_file_raises_error():
    with pytest.raises(FileNotFoundError):
        ClientModel(definition_loader=DefinitionFileLoader(definition_file="nonexisting.json"))


def test_non_existing_data_file_raises_error():
    with pytest.raises(FileNotFoundError):
        ClientModel(data_loader=DataFileLoader(data_file="nonexisting.json"))


def test_use_undefined_object(empty_definition_loader):
    with pytest.raises(AttributeError):
        ClientModel(definition_loader=empty_definition_loader)


def test_objects(empty_data_loader):
    model = ClientModel(data_loader=empty_data_loader)
    assert len(model.objects()) == 0, "should be empty"


def test_apply_with_invalid_parameter(model):
    with pytest.raises(AssertionError):
        model.apply(1)


def test_path_with_wrong_length(model):
    with pytest.raises(AttributeError):
        model.is_path_valid((1, 2, 3, 4,))


def test_path_with_invalid_elements(model):
    with pytest.raises(AssertionError):
        assert model.is_path_valid(('a', 3,))


def test_path_object_id_is_valid(model):
    assert model.is_path_valid((3,)), "path for objectID must be valid."


def test_path_object_id_and_instance_id_is_valid(model):
    assert model.is_path_valid((3, 0,)), "path for objectID with instanceID must be valid."


def test_path_object_id_instance_id_and_resource_id_is_valid(model):
    assert model.is_path_valid((3, 0, 1)), "path for objectID with instanceID must be valid."


def test_path_with_invalid_object(model):
    with pytest.raises(KeyError):
        assert model.resource(999999, 0, 0)


def test_path_with_invalid_instance(model):
    with pytest.raises(KeyError):
        assert model.resource(3, 1, 0)


def test_path_with_invalid_instance(model):
    with pytest.raises(KeyError):
        assert model.resource(3, 0, 99999)
