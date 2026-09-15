# Custom CV / SOP Templates

Configure templates manually in
`../.claude/skills/phd-application-assistant/04-sop-and-cv.md`. Document the source
extension, trusted local compile command, fonts, and page limit; ask the harness
to test compilation if that toolchain is available. No template-registration
command is implemented.

Keep only reusable templates with `[PLACEHOLDER]` tokens here. Personal content,
compiled output, and logs belong under ignored `documents/`, not this directory.
