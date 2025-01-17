# pseudonymiser
An app with a GUI that pseudonymises data in CSV files through hashing (SHA256). Inspired by [OpenPseudonymiser](https://github.com/drcjar/OpenPseudonymiser), but written in Python.

The app hashes user-specified columns of data, and saves the digest in a new CSV (along with the columns that were not chosen to be hashed). It will always use a salt, which is either user-provided or randomly-generated, and not saved by the app. There is an option to save a key file, which is a CSV that contains columns of data and its hash digest next to each other.

## Progress
This is a standalone piece of code that has yet been packaged for installation. Ideas for further development:
* Store salt in an encrypted way
* Hash collision handling
* Other methods of pseudonymisation
