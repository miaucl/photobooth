# Locale

To translate the photobooth, follow the steps below.

Make sure you have `gettext` installed.

```bash
sudo apt install gettext
```

## Extract text from source files

This pulls the most recent content from the source files.

```bash
xgettext photobooth/**/*.py -o photobooth/locale/messages.pot
```

## Create a new language setup

```bash
NEW_LANG=ex
mkdir -p photobooth/locale/$NEW_LANG/LC_MESSAGES/
msginit -i photobooth/locale/messages.pot --locale=$NEW_LANG -o photobooth/locale/$NEW_LANG/LC_MESSAGES/photobooth.po
```

## Bundle up into a binary file

```bash
NEW_LANG=ex
msgfmt photobooth/locale/$NEW_LANG/LC_MESSAGES/photobooth.po -o photobooth/locale/$NEW_LANG/LC_MESSAGES/photobooth.mo
```
