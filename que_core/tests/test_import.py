def test_importable():
    import que_core
    assert hasattr(que_core, "__all__")
