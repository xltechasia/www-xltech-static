#!/usr/bin/env bash
opl_dir="$HOME/git/openpracticelibrary"
xlt_dir="$HOME/git/www-xltech-static"
opl_content="$xlt_dir/content/opl"
opl_static="$xlt_dir/static/opl"

_error(){
  echo " **** ERROR: $@"
  exit 1
}

echo "Validating environment..."
if [ ! -d "$opl_dir" ]; then
  _error "OPL not @ $opl_dir"
  exit 1
fi

if [ ! -d "$xlt_dir" ]; then
  _error "XLT not @ $xlt_dir"
  exit 1
fi

mkdir -p "$opl_content"
if [ ! -d "$opl_content" ]; then
  _error "OPL Content not @ $opl_content"
  exit 1
fi

mkdir -p "$opl_static"
if [ ! -d "$opl_static" ]; then
  _error "OPL Content not @ $opl_static"
  exit 1
fi

echo "Copying over fixed items..."
for srcfile in "Gruntfile.js" "UI-UX" ; do
    cp -fR "$opl_dir/$srcfile" "$xlt_dir"
done

echo "Copying over Static items..."
cp -fR "$opl_dir/static/" "$opl_static"

