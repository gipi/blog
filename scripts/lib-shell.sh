
DEFAULT_COLOR_SETTING='\e[1m'
OK_COLOR=${DEFAULT_COLOR_SETTING}'\e[32m'
WARNING_COLOR=${DEFAULT_COLOR_SETTING}'\e[36m'
FAIL_COLOR=${DEFAULT_COLOR_SETTING}'\e[31m'
RESET_COLOR='\e[0m'

ok_message () {
	echo -e ${OK_COLOR}$1${RESET_COLOR}
}

warning_message () {
	echo -e ${WARNING_COLOR}$1${RESET_COLOR}
}

fail_message () {
	echo -e ${FAIL_COLOR}$1${RESET_COLOR}
}

message () {
	echo -e "$1"
}
