# Developers instructions #

## Running the tests locally ##

1. Make sure you have the following installed:
  - [Python](https://www.python.org) (any version >2.7 should work),
  - bash, make and sed (needed for the build scripts).
2. Create a test **craft ai** project and retrieve its **write token**.
3. At the root of your local clone, create a file named `.env` with the following content.

  ```
  CRAFT_TOKEN=<retrieved_token>
  ```

4. Init the git submodules (needed for the interpreter tests)
  ```console
  $ git submodule init
  $ git submodule update
  ```

5. Install the dependencies. For the following steps, you may want use in a Python virtual environment.

  ```console
  $ make init
  ```

6. Run the tests!

  ```console
  $ make test
  ```

## Releasing a new version (needs administrator rights) ##

1. Make sure the build of the master branch is passing

  [![Build](https://img.shields.io/travis/craft-ai/craft-ai-client-python/master.svg?style=flat-square)](https://travis-ci.org/craft-ai/craft-ai-client-python)

2. Checkout the master branch locally.

  ```console
  $ git fetch
  $ git checkout master
  $ git reset --hard origin/master
  ```

3. Update `README.md` from **craft ai** documentation found
   at <https://beta.craft.ai/doc/python>.


  ```console
  $ make update-readme
  ```

  > This will create a git commit.


4. Increment the version in `craft_ai/__init__.py` and move _Unreleased_ section
   of `CHANGELOG.md` to a newly created section for this version.

  ```console
  $ make version-increment-patch
  ```

  `make version-increment-minor` and `make version-increment-major` are
  also available - see [semver](http://semver.org) for a guideline on when to
  use which.

  > This will create a git commit and a git tag.

5. Push everything!

  ```console
  $ git push origin master
  $ git push --tags
  ```

  > This will trigger the publishing of this new version to
  > [PyPI](https://pypi.python.org/pypi/craft-ai) by
  > [Travis](https://travis-ci.org/craft-ai/craft-ai-client-python)
