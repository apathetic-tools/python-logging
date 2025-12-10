# CHANGELOG

<!-- version list -->

## v0.15.0 (2025-12-10)

### Features

- **logger**: Implement root logger replacement with handler/level porting
  ([`9baa0da`](https://github.com/apathetic-tools/python-logging/commit/9baa0da16fa207dcbdd35c3441d7c80e9d01f669))


## v0.14.0 (2025-12-10)

### Features

- **api**: Add getRootLogger function
  ([`6213c19`](https://github.com/apathetic-tools/python-logging/commit/6213c194fb66fd16878a303cd59f79228c1949fe))


## v0.13.0 (2025-12-10)

### Features

- **api**: Add set_level_convenience and use_level_minimum functions
  ([`173120d`](https://github.com/apathetic-tools/python-logging/commit/173120d25a4fa23a1852e1c8bf07afe22298962b))


## v0.12.0 (2025-12-10)

### Features

- **api**: Add test() module-level function
  ([`6ca9fb1`](https://github.com/apathetic-tools/python-logging/commit/6ca9fb1ce405c8a8a87e3b5411684c1c0721761b))


## v0.11.0 (2025-12-09)

### Features

- **logger**: Add set_level_and_propagate and use_level_and_propagate methods
  ([`4afb61c`](https://github.com/apathetic-tools/python-logging/commit/4afb61c572d56638669fe60769f8f07196c1f554))


## v0.10.0 (2025-12-09)

### Features

- **logger**: Add usePropagate context manager
  ([`3425260`](https://github.com/apathetic-tools/python-logging/commit/3425260fb1370021a321986d2338db54771b9ce1))


## v0.9.0 (2025-12-09)

### Features

- **logger**: Register custom levels in apathetic_logging namespace
  ([`359ef0a`](https://github.com/apathetic-tools/python-logging/commit/359ef0ab36aa15104454f8b3ec2375d916a95d39))


## v0.8.0 (2025-12-09)

### Features

- **logger**: Rename ensureHandlers to manageHandlers and add handler management
  ([`0daafc3`](https://github.com/apathetic-tools/python-logging/commit/0daafc3e41132202e1e6ce52cac1c98a121623c4))

### Refactoring

- **core**: Update logger implementation and tests
  ([`988c159`](https://github.com/apathetic-tools/python-logging/commit/988c1596bad187ebb3c5e6135b11ff64c4632412))


## v0.7.0 (2025-12-09)

### Build System

- **config**: Update tooling scripts and test configuration
  ([`9ef9d55`](https://github.com/apathetic-tools/python-logging/commit/9ef9d55b8f69ccbdfa07e96ee8554211cf5feb55))

### Features

- **logger**: Add setPropagate method and root logger constants
  ([`4573e08`](https://github.com/apathetic-tools/python-logging/commit/4573e08dd170e7123ede2dfa72fccd70479d8875))


## v0.6.2 (2025-12-08)

### Bug Fixes

- **core**: Remove space in pyright ignore comment
  ([`3b20e15`](https://github.com/apathetic-tools/python-logging/commit/3b20e156bcf71d8e6f0b2fc62f7e6f346b38ce17))

### Chores

- **deps**: Update dependency versions in poetry.lock
  ([`f3ca19e`](https://github.com/apathetic-tools/python-logging/commit/f3ca19e5cd469f510a7f2891bf6518d813b91fba))

### Testing

- **core**: Add test for isEnabledFor cache invalidation on setLevel
  ([`0f4603a`](https://github.com/apathetic-tools/python-logging/commit/0f4603ae3624b60f6db4a5120ae9b6c7414756fd))


## v0.6.1 (2025-12-08)

### Bug Fixes

- **tests**: Resolve stitched build test failures with updated patch_everywhere
  ([`8821205`](https://github.com/apathetic-tools/python-logging/commit/88212051feb429ed2223d7a42530225ff957b163))

### Continuous Integration

- **release**: Install package root in workflow
  ([`face149`](https://github.com/apathetic-tools/python-logging/commit/face14909777abc15fe8760a78df10b8304a79b0))

- **release**: Make .py and .pyz file attachments optional
  ([`440f168`](https://github.com/apathetic-tools/python-logging/commit/440f168b2afe76893ca74d6ccc05d049988def06))

### Documentation

- Update warning note style and add to index page
  ([`0447182`](https://github.com/apathetic-tools/python-logging/commit/0447182dfb6649d7d1bfe71c724fb9ac4151c118))

- **api**: Update safeTrace and SAFE_TRACE_ENABLED documentation
  ([`97a2888`](https://github.com/apathetic-tools/python-logging/commit/97a2888eddbfd7faf0b0c9e33e9a86fcf93af204))


## v0.6.0 (2025-12-05)

### Features

- **logging**: Add minimal level as deprecated alias for brief
  ([`e739dbf`](https://github.com/apathetic-tools/python-logging/commit/e739dbfbe5f40361603863050c76bca673f8b0d8))

- **safe-logging**: Add isSafeTraceEnabled method
  ([`4ff04e5`](https://github.com/apathetic-tools/python-logging/commit/4ff04e52d933accb1bf759a8ced8a8c0b6048d72))


## v0.5.0 (2025-12-05)

### Features

- **tests**: Skip zipapp tests until zipbundler replaces shiv
  ([`d491f0e`](https://github.com/apathetic-tools/python-logging/commit/d491f0e3962bf4403992b8a564ffab878928b45d))


## v0.4.0 (2025-12-05)

### Chores

- **deps**: Bump actions/checkout from 5 to 6
  ([#1](https://github.com/apathetic-tools/python-logging/pull/1),
  [`c2fe742`](https://github.com/apathetic-tools/python-logging/commit/c2fe742ac3dd1050abcf648ee4dda46ec39c9a63))

### Features

- **api**: Rename MINIMAL_LEVEL to BRIEF_LEVEL and minimal() to brief()
  ([`842b696`](https://github.com/apathetic-tools/python-logging/commit/842b69640150ad67b70a6182c0d825e26332b69b))

### Refactoring

- **ci**: Rename workflow files for clarity
  ([`356e1eb`](https://github.com/apathetic-tools/python-logging/commit/356e1eb4e16a94fb0500bd39bf169f8dfb3a0208))


## v0.3.2 (2025-11-28)

### Bug Fixes

- **tests**: Resolve lint errors and debug test filter bug
  ([`bca70df`](https://github.com/apathetic-tools/python-logging/commit/bca70df85deff5ab0dad36c197d95464ac0aa73e))


## v0.3.1 (2025-11-28)

### Bug Fixes

- **workflows**: Correct YAML indentation in publish workflow
  ([`4be6e43`](https://github.com/apathetic-tools/python-logging/commit/4be6e435a790b1eee63af4a5122f7efea0fdabca))


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
