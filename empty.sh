#!/bin/sh

#
# Generated on Tue May 21 21:49:22 PDT 2024
# Start of user configurable variables
#
LANG=C
export LANG

#Trap to cleanup cookie file in case of unexpected exits.
trap 'rm -f $COOKIE_FILE; exit 1' 1 2 3 6 

# SSO username 
printf 'SSO User Name:' 
read SSO_USERNAME

# Path to wget command
WGET=/usr/bin/wget

# Log directory and file
LOGDIR=.
LOGFILE=$LOGDIR/wgetlog-$(date +%m-%d-%y-%H:%M).log

# Print wget version info 
echo "Wget version info: 
------------------------------
$($WGET -V) 
------------------------------" > "$LOGFILE" 2>&1 

# Location of cookie file 
COOKIE_FILE=$(mktemp -t wget_sh_XXXXXX) >> "$LOGFILE" 2>&1 
if [ $? -ne 0 ] || [ -z "$COOKIE_FILE" ] 
then 
 echo "Temporary cookie file creation failed. See $LOGFILE for more details." |  tee -a "$LOGFILE" 
 exit 1 
fi 
echo "Created temporary cookie file $COOKIE_FILE" >> "$LOGFILE" 

# Output directory and file
OUTPUT_DIR=.
#
# End of user configurable variable
#

# The following command to authenticate uses HTTPS. This will work only if the wget in the environment
# where this script will be executed was compiled with OpenSSL.
# 
 $WGET  --secure-protocol=auto --save-cookies="$COOKIE_FILE" --keep-session-cookies --http-user "$SSO_USERNAME" --ask-password  "https://edelivery.oracle.com/osdc/cliauth" -a "$LOGFILE"

# Verify if authentication is successful 
if [ $? -ne 0 ] 
then 
 echo "Authentication failed with the given credentials." | tee -a "$LOGFILE"
 echo "Please check logfile: $LOGFILE for more details." 
else
 echo "Authentication is successful. Proceeding with downloads..." >> "$LOGFILE" 
 $WGET  --load-cookies="$COOKIE_FILE" --save-cookies="$COOKIE_FILE" --keep-session-cookies "https://edelivery.oracle.com/osdc/softwareDownload?fileName=V975332-01.zip&token=QmYvTlZUNUdmaGFrTFhVeVJEam41USE6OiFmaWxlSWQ9OTk3ODIzMDAmZmlsZVNldENpZD04NjUwNTcmcmVsZWFzZUNpZHM9ODYwNjAwJnBsYXRmb3JtQ2lkcz02MCZkb3dubG9hZFR5cGU9OTU3NjEmYWdyZWVtZW50SWQ9MTA3OTIyOTYmZW1haWxBZGRyZXNzPW1hZGR5Y3JlYXplckBnbWFpbC5jb20mdXNlck5hbWU9RVBELU1BRERZQ1JFQVpFUkBHTUFJTC5DT00maXBBZGRyZXNzPTIwMy4xOTIuMjQ0LjE0MyZ1c2VyQWdlbnQ9TW96aWxsYS81LjAgKGlQaG9uZTsgQ1BVIGlQaG9uZSBPUyAxNl83XzcgbGlrZSBNYWMgT1MgWCkgQXBwbGVXZWJLaXQvNjA1LjEuMTUgKEtIVE1MLCBsaWtlIEdlY2tvKSBWZXJzaW9uLzE2LjYgTW9iaWxlLzE1RTE0OCBTYWZhcmkvNjA0LjEmY291bnRyeUNvZGU9SU4" -O "$OUTPUT_DIR/V975332-01.zip" >> "$LOGFILE" 2>&1 
 $WGET  --load-cookies="$COOKIE_FILE" --save-cookies="$COOKIE_FILE" --keep-session-cookies "https://edelivery.oracle.com/osdc/softwareDownload?fileName=V975333-01.iso&token=bGovV2hnM1NydHhlaGVPK1doVjJvQSE6OiFmaWxlSWQ9OTk3ODIzMDEmZmlsZVNldENpZD04NjUwOTgmcmVsZWFzZUNpZHM9ODYwNjAwJnBsYXRmb3JtQ2lkcz02MCZkb3dubG9hZFR5cGU9OTU3NjEmYWdyZWVtZW50SWQ9MTA3OTIyOTYmZW1haWxBZGRyZXNzPW1hZGR5Y3JlYXplckBnbWFpbC5jb20mdXNlck5hbWU9RVBELU1BRERZQ1JFQVpFUkBHTUFJTC5DT00maXBBZGRyZXNzPTIwMy4xOTIuMjQ0LjE0MyZ1c2VyQWdlbnQ9TW96aWxsYS81LjAgKGlQaG9uZTsgQ1BVIGlQaG9uZSBPUyAxNl83XzcgbGlrZSBNYWMgT1MgWCkgQXBwbGVXZWJLaXQvNjA1LjEuMTUgKEtIVE1MLCBsaWtlIEdlY2tvKSBWZXJzaW9uLzE2LjYgTW9iaWxlLzE1RTE0OCBTYWZhcmkvNjA0LjEmY291bnRyeUNvZGU9SU4" -O "$OUTPUT_DIR/V975333-01.iso" >> "$LOGFILE" 2>&1 
 $WGET  --load-cookies="$COOKIE_FILE" --save-cookies="$COOKIE_FILE" --keep-session-cookies "https://edelivery.oracle.com/osdc/softwareDownload?fileName=V975334-01.zip&token=U01vTjJTOUwxRU5rcDJvZXZHQzZoUSE6OiFmaWxlSWQ9OTk3ODIyNzAmZmlsZVNldENpZD04NjQ5NzEmcmVsZWFzZUNpZHM9ODYwNjAwJnBsYXRmb3JtQ2lkcz02MCZkb3dubG9hZFR5cGU9OTU3NjEmYWdyZWVtZW50SWQ9MTA3OTIyOTYmZW1haWxBZGRyZXNzPW1hZGR5Y3JlYXplckBnbWFpbC5jb20mdXNlck5hbWU9RVBELU1BRERZQ1JFQVpFUkBHTUFJTC5DT00maXBBZGRyZXNzPTIwMy4xOTIuMjQ0LjE0MyZ1c2VyQWdlbnQ9TW96aWxsYS81LjAgKGlQaG9uZTsgQ1BVIGlQaG9uZSBPUyAxNl83XzcgbGlrZSBNYWMgT1MgWCkgQXBwbGVXZWJLaXQvNjA1LjEuMTUgKEtIVE1MLCBsaWtlIEdlY2tvKSBWZXJzaW9uLzE2LjYgTW9iaWxlLzE1RTE0OCBTYWZhcmkvNjA0LjEmY291bnRyeUNvZGU9SU4" -O "$OUTPUT_DIR/V975334-01.zip" >> "$LOGFILE" 2>&1 
 $WGET  --load-cookies="$COOKIE_FILE" --save-cookies="$COOKIE_FILE" --keep-session-cookies "https://edelivery.oracle.com/osdc/softwareDownload?fileName=V975335-01.iso&token=MUdsaEVTc0hLNFNQUXJWZGNlNGhNdyE6OiFmaWxlSWQ9OTk3ODIzMDQmZmlsZVNldENpZD04NjQ5NzImcmVsZWFzZUNpZHM9ODYwNjAwJnBsYXRmb3JtQ2lkcz02MCZkb3dubG9hZFR5cGU9OTU3NjEmYWdyZWVtZW50SWQ9MTA3OTIyOTYmZW1haWxBZGRyZXNzPW1hZGR5Y3JlYXplckBnbWFpbC5jb20mdXNlck5hbWU9RVBELU1BRERZQ1JFQVpFUkBHTUFJTC5DT00maXBBZGRyZXNzPTIwMy4xOTIuMjQ0LjE0MyZ1c2VyQWdlbnQ9TW96aWxsYS81LjAgKGlQaG9uZTsgQ1BVIGlQaG9uZSBPUyAxNl83XzcgbGlrZSBNYWMgT1MgWCkgQXBwbGVXZWJLaXQvNjA1LjEuMTUgKEtIVE1MLCBsaWtlIEdlY2tvKSBWZXJzaW9uLzE2LjYgTW9iaWxlLzE1RTE0OCBTYWZhcmkvNjA0LjEmY291bnRyeUNvZGU9SU4" -O "$OUTPUT_DIR/V975335-01.iso" >> "$LOGFILE" 2>&1 
 $WGET  --load-cookies="$COOKIE_FILE" --save-cookies="$COOKIE_FILE" --keep-session-cookies "https://edelivery.oracle.com/osdc/softwareDownload?fileName=V975336-01.zip&token=bEFyOU10c0N6Y21KQWRhQ1NXQTVjUSE6OiFmaWxlSWQ9OTk3ODIyNzkmZmlsZVNldENpZD04NjUxMTMmcmVsZWFzZUNpZHM9ODYwNjAwJnBsYXRmb3JtQ2lkcz02MCZkb3dubG9hZFR5cGU9OTU3NjEmYWdyZWVtZW50SWQ9MTA3OTIyOTYmZW1haWxBZGRyZXNzPW1hZGR5Y3JlYXplckBnbWFpbC5jb20mdXNlck5hbWU9RVBELU1BRERZQ1JFQVpFUkBHTUFJTC5DT00maXBBZGRyZXNzPTIwMy4xOTIuMjQ0LjE0MyZ1c2VyQWdlbnQ9TW96aWxsYS81LjAgKGlQaG9uZTsgQ1BVIGlQaG9uZSBPUyAxNl83XzcgbGlrZSBNYWMgT1MgWCkgQXBwbGVXZWJLaXQvNjA1LjEuMTUgKEtIVE1MLCBsaWtlIEdlY2tvKSBWZXJzaW9uLzE2LjYgTW9iaWxlLzE1RTE0OCBTYWZhcmkvNjA0LjEmY291bnRyeUNvZGU9SU4" -O "$OUTPUT_DIR/V975336-01.zip" >> "$LOGFILE" 2>&1 
 $WGET  --load-cookies="$COOKIE_FILE" --save-cookies="$COOKIE_FILE" --keep-session-cookies "https://edelivery.oracle.com/osdc/softwareDownload?fileName=V975363-01.iso&token=VVdsaWlBblNSL3B0Qmd0LzhteHFHdyE6OiFmaWxlSWQ9OTk4Njc3NDYmZmlsZVNldENpZD04NjU1NDEmcmVsZWFzZUNpZHM9ODYwNjAwJnBsYXRmb3JtQ2lkcz02MCZkb3dubG9hZFR5cGU9OTU3NjEmYWdyZWVtZW50SWQ9MTA3OTIyOTYmZW1haWxBZGRyZXNzPW1hZGR5Y3JlYXplckBnbWFpbC5jb20mdXNlck5hbWU9RVBELU1BRERZQ1JFQVpFUkBHTUFJTC5DT00maXBBZGRyZXNzPTIwMy4xOTIuMjQ0LjE0MyZ1c2VyQWdlbnQ9TW96aWxsYS81LjAgKGlQaG9uZTsgQ1BVIGlQaG9uZSBPUyAxNl83XzcgbGlrZSBNYWMgT1MgWCkgQXBwbGVXZWJLaXQvNjA1LjEuMTUgKEtIVE1MLCBsaWtlIEdlY2tvKSBWZXJzaW9uLzE2LjYgTW9iaWxlLzE1RTE0OCBTYWZhcmkvNjA0LjEmY291bnRyeUNvZGU9SU4" -O "$OUTPUT_DIR/V975363-01.iso" >> "$LOGFILE" 2>&1 
 $WGET  --load-cookies="$COOKIE_FILE" --save-cookies="$COOKIE_FILE" --keep-session-cookies "https://edelivery.oracle.com/osdc/softwareDownload?fileName=V975364-01.iso&token=TmlKUnNaeFNTVWN1RitmejlWdi9HZyE6OiFmaWxlSWQ9OTk4Njc3NDgmZmlsZVNldENpZD04NjU1NDImcmVsZWFzZUNpZHM9ODYwNjAwJnBsYXRmb3JtQ2lkcz02MCZkb3dubG9hZFR5cGU9OTU3NjEmYWdyZWVtZW50SWQ9MTA3OTIyOTYmZW1haWxBZGRyZXNzPW1hZGR5Y3JlYXplckBnbWFpbC5jb20mdXNlck5hbWU9RVBELU1BRERZQ1JFQVpFUkBHTUFJTC5DT00maXBBZGRyZXNzPTIwMy4xOTIuMjQ0LjE0MyZ1c2VyQWdlbnQ9TW96aWxsYS81LjAgKGlQaG9uZTsgQ1BVIGlQaG9uZSBPUyAxNl83XzcgbGlrZSBNYWMgT1MgWCkgQXBwbGVXZWJLaXQvNjA1LjEuMTUgKEtIVE1MLCBsaWtlIEdlY2tvKSBWZXJzaW9uLzE2LjYgTW9iaWxlLzE1RTE0OCBTYWZhcmkvNjA0LjEmY291bnRyeUNvZGU9SU4" -O "$OUTPUT_DIR/V975364-01.iso" >> "$LOGFILE" 2>&1 
 $WGET  --load-cookies="$COOKIE_FILE" --save-cookies="$COOKIE_FILE" --keep-session-cookies "https://edelivery.oracle.com/osdc/softwareDownload?fileName=V975365-01.iso&token=ZzhEaE5HU0xKc2t2TVY5M2E4alN2USE6OiFmaWxlSWQ9OTk4Njc3ODMmZmlsZVNldENpZD04NjU1NzkmcmVsZWFzZUNpZHM9ODYwNjAwJnBsYXRmb3JtQ2lkcz02MCZkb3dubG9hZFR5cGU9OTU3NjEmYWdyZWVtZW50SWQ9MTA3OTIyOTYmZW1haWxBZGRyZXNzPW1hZGR5Y3JlYXplckBnbWFpbC5jb20mdXNlck5hbWU9RVBELU1BRERZQ1JFQVpFUkBHTUFJTC5DT00maXBBZGRyZXNzPTIwMy4xOTIuMjQ0LjE0MyZ1c2VyQWdlbnQ9TW96aWxsYS81LjAgKGlQaG9uZTsgQ1BVIGlQaG9uZSBPUyAxNl83XzcgbGlrZSBNYWMgT1MgWCkgQXBwbGVXZWJLaXQvNjA1LjEuMTUgKEtIVE1MLCBsaWtlIEdlY2tvKSBWZXJzaW9uLzE2LjYgTW9iaWxlLzE1RTE0OCBTYWZhcmkvNjA0LjEmY291bnRyeUNvZGU9SU4" -O "$OUTPUT_DIR/V975365-01.iso" >> "$LOGFILE" 2>&1 
 $WGET  --load-cookies="$COOKIE_FILE" --save-cookies="$COOKIE_FILE" --keep-session-cookies "https://edelivery.oracle.com/osdc/softwareDownload?fileName=V975366-01.iso&token=SGl6MkxsZEZmUnhsNnBKdHZ1ZUZTUSE6OiFmaWxlSWQ9OTk4Njc3NjImZmlsZVNldENpZD04NjU1NDMmcmVsZWFzZUNpZHM9ODYwNjAwJnBsYXRmb3JtQ2lkcz02MCZkb3dubG9hZFR5cGU9OTU3NjEmYWdyZWVtZW50SWQ9MTA3OTIyOTYmZW1haWxBZGRyZXNzPW1hZGR5Y3JlYXplckBnbWFpbC5jb20mdXNlck5hbWU9RVBELU1BRERZQ1JFQVpFUkBHTUFJTC5DT00maXBBZGRyZXNzPTIwMy4xOTIuMjQ0LjE0MyZ1c2VyQWdlbnQ9TW96aWxsYS81LjAgKGlQaG9uZTsgQ1BVIGlQaG9uZSBPUyAxNl83XzcgbGlrZSBNYWMgT1MgWCkgQXBwbGVXZWJLaXQvNjA1LjEuMTUgKEtIVE1MLCBsaWtlIEdlY2tvKSBWZXJzaW9uLzE2LjYgTW9iaWxlLzE1RTE0OCBTYWZhcmkvNjA0LjEmY291bnRyeUNvZGU9SU4" -O "$OUTPUT_DIR/V975366-01.iso" >> "$LOGFILE" 2>&1 
 $WGET --load-cookies="$COOKIE_FILE" "https://edelivery.oracle.com/osdc/softwareDownload?fileName=V975367-01.iso&token=RngwN3creTdyNW5raERCS3RWTll5dyE6OiFmaWxlSWQ9OTk4Njc3NjUmZmlsZVNldENpZD04NjU2MTMmcmVsZWFzZUNpZHM9ODYwNjAwJnBsYXRmb3JtQ2lkcz02MCZkb3dubG9hZFR5cGU9OTU3NjEmYWdyZWVtZW50SWQ9MTA3OTIyOTYmZW1haWxBZGRyZXNzPW1hZGR5Y3JlYXplckBnbWFpbC5jb20mdXNlck5hbWU9RVBELU1BRERZQ1JFQVpFUkBHTUFJTC5DT00maXBBZGRyZXNzPTIwMy4xOTIuMjQ0LjE0MyZ1c2VyQWdlbnQ9TW96aWxsYS81LjAgKGlQaG9uZTsgQ1BVIGlQaG9uZSBPUyAxNl83XzcgbGlrZSBNYWMgT1MgWCkgQXBwbGVXZWJLaXQvNjA1LjEuMTUgKEtIVE1MLCBsaWtlIEdlY2tvKSBWZXJzaW9uLzE2LjYgTW9iaWxlLzE1RTE0OCBTYWZhcmkvNjA0LjEmY291bnRyeUNvZGU9SU4" -O "$OUTPUT_DIR/V975367-01.iso" >> "$LOGFILE" 2>&1 
fi 

# Cleanup
rm -f "$COOKIE_FILE" 
echo "Removed temporary cookie file $COOKIE_FILE" >> "$LOGFILE" 