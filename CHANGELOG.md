# CHANGELOG

<!-- version list -->

## v0.3.0 (2025-11-28)

### Bug Fixes

- **ci**: Enable verbose output for TestPyPI publish debugging
  ([`a015fa4`](https://github.com/apathetic-tools/python-logging/commit/a015fa469efce3f39e3a38bc127c6019423946b0))

- **ci**: Improve TestPyPI publish error handling
  ([`5b9cba0`](https://github.com/apathetic-tools/python-logging/commit/5b9cba08cdf1237dcf9c7fbcb425bc7b25fd36ce))

- **ci**: Update publish workflow to match pypa documentation format
  ([`748bfd7`](https://github.com/apathetic-tools/python-logging/commit/748bfd7e748f09efa9ea38e41b65c3be35f85e49))

- **metadata**: Fix invalid PyPI classifier and add validation
  ([`f116dd1`](https://github.com/apathetic-tools/python-logging/commit/f116dd1570e363e87fac1ddd7f1af11fb19250ee))

### Features

- **ci**: Integrate publish workflow with release workflow
  ([`7763808`](https://github.com/apathetic-tools/python-logging/commit/7763808be3c4b867dc5ad70f2c93b7799b9b3bc4))


## v0.2.3 (2025-11-27)

### Bug Fixes

- **release**: Prevent semantic-release from uploading custom files and improve error handling
  ([`38aeeb4`](https://github.com/apathetic-tools/python-logging/commit/38aeeb4275a1e356b3abf88f084d0963830aef20))

- **release**: Remove build_command config from semantic-release
  ([`7c33438`](https://github.com/apathetic-tools/python-logging/commit/7c33438d7d119d09991dd87b26b4b00d407fad81))

### Chores

- **pyproject**: Update keywords and classifiers
  ([`89365b5`](https://github.com/apathetic-tools/python-logging/commit/89365b5912c710a65f016b6fc304180f6c84bdd8))

### Documentation

- Update project description and tagline
  ([`95ea9f1`](https://github.com/apathetic-tools/python-logging/commit/95ea9f1802e29aebb94418e23f4158e539937fcf))

### Refactoring

- **ci**: Use pypa/gh-action-pypi-publish for publishing
  ([`a8bd8ee`](https://github.com/apathetic-tools/python-logging/commit/a8bd8eeafeeef14fb272c2b23fc4fd7bf24798be))

- **core**: Rename _is_standalone to _apathetic_logging_is_standalone
  ([`97f6a7f`](https://github.com/apathetic-tools/python-logging/commit/97f6a7f050c66625fdc90cf83227dd34cab61b51))

- **publish**: Clean up PyPI publishing workflow
  ([`d148024`](https://github.com/apathetic-tools/python-logging/commit/d148024743462b2af63670fdddfee10bae648e0f))


## v0.2.2 (2025-11-25)

### Bug Fixes

- **release**: Remove invalid --no-vcs-release flag from semantic-release
  ([`3dae602`](https://github.com/apathetic-tools/python-logging/commit/3dae602ea216ffc7b038947c8f7af2e1b272e14d))


## v0.2.1 (2025-11-25)

### Bug Fixes

- **release**: Improve version detection pattern for semantic-release output
  ([`3f9451f`](https://github.com/apathetic-tools/python-logging/commit/3f9451ff446669633a5d6cbb2d210c158e61cea8))


## v0.2.0 (2025-11-25)

### Bug Fixes

- **ci**: Add GH_TOKEN environment variable for semantic-release
  ([`4bf912e`](https://github.com/apathetic-tools/python-logging/commit/4bf912ecc2e01808e2aac2ae16b4563442f7193e))

- **ci**: Correct semantic-release remote configuration format
  ([`272a08c`](https://github.com/apathetic-tools/python-logging/commit/272a08c76d71708fd166b497561df57e943fa785))

- **release**: Add step id for release output reference
  ([`5c449a1`](https://github.com/apathetic-tools/python-logging/commit/5c449a1895916501fd30128a4a2fa44c4fc2b635))

- **release**: Correct upload_to_vcs_release configuration setting
  ([`26e612c`](https://github.com/apathetic-tools/python-logging/commit/26e612c9d9afa64eac700b256385c1e84c2744a9))

- **release**: Disable semantic-release asset upload to prevent 422 errors
  ([`a254d04`](https://github.com/apathetic-tools/python-logging/commit/a254d04834adfd47bb1f612d655506785f0445d4))

- **release**: Disable semantic-release build and dist discovery
  ([`79b304e`](https://github.com/apathetic-tools/python-logging/commit/79b304e68b9f1e8b8e335d9ac4123c17067a044c))

- **release**: Enable allow_zero_version for major_on_zero configuration
  ([`44855f2`](https://github.com/apathetic-tools/python-logging/commit/44855f25c8ad377eb2d826df5e49b895dee95dd2))

- **release**: Split semantic-release into version and publish steps
  ([`f887e31`](https://github.com/apathetic-tools/python-logging/commit/f887e311034912efd5f057fcbdbb56bcf5cebfd5))

- **release**: Update release detection logic after disabling semantic-release build
  ([`9e85f2d`](https://github.com/apathetic-tools/python-logging/commit/9e85f2df4583394847915ebe8c681745bcb19b3b))

### Chores

- **config**: Add VSCode settings and improve release workflow
  ([`e453237`](https://github.com/apathetic-tools/python-logging/commit/e4532372b2d26ef330b27628387930ba26b70668))

- **deps**: Update dependencies to latest versions
  ([`7d0956f`](https://github.com/apathetic-tools/python-logging/commit/7d0956fc2b2fefcf59e8924603c1572b6835b617))

### Documentation

- Streamline CONTRIBUTING.md and add detailed publishing to docs
  ([`2f599ed`](https://github.com/apathetic-tools/python-logging/commit/2f599ed3fc36b7a70e925bc3a8e299dc74aaa217))

- **decisions**: Add Astro to options considered for DEC 12
  ([`351ade7`](https://github.com/apathetic-tools/python-logging/commit/351ade7cebbbbfd0b386bf1d7d1da0442a28935c))

- **decisions**: Add five new decision records with git history dates
  ([`9381e68`](https://github.com/apathetic-tools/python-logging/commit/9381e685486762d1679b8420262249e1edcbd0ce))

- **decisions**: Renumber decisions in reverse chronological order
  ([`ac8e52f`](https://github.com/apathetic-tools/python-logging/commit/ac8e52fed171fc7d0d32d504f2444b034ccf998d))

### Features

- **docs**: Update README description to mention context support
  ([`c4d99aa`](https://github.com/apathetic-tools/python-logging/commit/c4d99aaa1ec41423c76e60ae649dd022b6b3f3bf))

- **package**: Add py.typed marker for type checking support
  ([`17e18aa`](https://github.com/apathetic-tools/python-logging/commit/17e18aa23279eb0c44fe3343fd412f64b4b04404))

- **release**: Setup python-semantic-release for automated releases
  ([`a7c08c7`](https://github.com/apathetic-tools/python-logging/commit/a7c08c71cc51fad14cf5a3214c789f7284b4028b))

- **test**: Add zipapp as third runtime mode in runtime_swap
  ([`702187b`](https://github.com/apathetic-tools/python-logging/commit/702187bf9bfb059806b4c77f91b8122d020c701e))

### Refactoring

- **env**: Migrate from pyenv to mise for version management
  ([`36cf298`](https://github.com/apathetic-tools/python-logging/commit/36cf2984d9eb95b8614acf9de9680564ee9796c0))

### Testing

- **build**: Add shiv zipapp tests and refactor build tests
  ([`3609cad`](https://github.com/apathetic-tools/python-logging/commit/3609cad0cccff88f39248add2db3ef0d88d64ea7))


## v0.1.1 (2025-11-24)

### Bug Fixes

- **logging**: Pass through *args and **kwargs in wrapper functions
  ([`0977b5a`](https://github.com/apathetic-tools/python-logging/commit/0977b5a5a47353e09d0f84dc5d69e6422d8d1c9e))

### Chores

- Bump version to 0.1.1
  ([`7edf444`](https://github.com/apathetic-tools/python-logging/commit/7edf44431f1719c6704d75089a18add53eb1d0be))


## v0.1.0 (2025-11-24)

- Initial Release
