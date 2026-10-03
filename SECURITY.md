# Security

This is a trusted-network developer example. Raw TCP input and the HTTP page are
unencrypted and unauthenticated; the WebRTC leg alone encrypts media. Limit the
published ports to intended interfaces and devices. Do not expose the stack to
the internet without a separate access-control and transport design.

Report vulnerabilities through GitHub's private vulnerability reporting feature
instead of public issues. Include affected versions and a minimal reproduction,
without credentials or captured private screen content. Only the current default
branch is maintained.
