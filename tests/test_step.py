def test_reload_script(dataset):

    STR_BEFORE = "test-before-modif"
    STR_AFTER = "test-after-modif"

    step = dataset.HDC.behavior.steps.first()
    assert step.script.test_modif() == STR_BEFORE

    script_path = dataset._scripts_path / "behavior" / "scores.py"
    script_path.write_text(script_path.read_text().replace(STR_BEFORE, STR_AFTER))

    step = dataset.HDC.behavior.steps.first()
    assert step.script.test_modif() == STR_AFTER
