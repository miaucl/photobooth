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

## Update a language with new terms

```bash
export LOCALE_LANG=ex
msgmerge photobooth/locale/$LOCALE_LANG/LC_MESSAGES/photobooth.po photobooth/locale/messages.pot -o photobooth/locale/$LOCALE_LANG/LC_MESSAGES/photobooth.po
```

## Create a new language setup

```bash
export LOCALE_LANG=ex
mkdir -p photobooth/locale/$LOCALE_LANG/LC_MESSAGES/
msginit -i photobooth/locale/messages.pot --locale=$LOCALE_LANG -o photobooth/locale/$LOCALE_LANG/LC_MESSAGES/photobooth.po
```

## Bundle up into a binary file

```bash
export LOCALE_LANG=ex
msgfmt photobooth/locale/$LOCALE_LANG/LC_MESSAGES/photobooth.po -o photobooth/locale/$LOCALE_LANG/LC_MESSAGES/photobooth.mo
```
