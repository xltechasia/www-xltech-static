#!/usr/bin/env bash
opl_dir = "$HOME/git/openpracticelibrary"
xlt_dir = "$HOME/git/www-xltech-static"
opl_content = "$xlt_dir/content/opl"

_error(){
  echo " **** ERROR: $errmsg"
  exit 1
}

echo "Validatinmg environment...""
if [ ! -d "$opl_dir" ]; then
  $errmsg = "OPL not @ $opl_dir"
  _error()
  exit 1
fi

if [ ! -d "$xlt_dir" ]; then
  $errmsg = "XLT not @ $xlt_dir"
  _error()
  exit 1
fi

mkdir -p "$opl_content"

if [ ! -d "$opl_content" ]; then
  $errmsg = "OPL Content not @ $opl_content"
  _error()
  exit 1
fi

