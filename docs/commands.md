# Overview

This document goes over the list of commands offered by the bot, giving the
requirements of each of these commands from a user perspective

# Status Commands

## /add_status_user

This command can be run in a group chat or in a private chat. The idea is for a
user to be able to add the online status's of a specific person's Xbox Live,
PSN, and Steam accounts.

## /modify_status_user

This requirements of this command has two separate audiences.

### **Group Admins**

Group admins need to have the ability to remove all status users that are a
part of the group they administrate, even if they don't own that status user.
However, they should NOT have the ability to modify that status user.

### **Normal Users**

Normal users should be able to edit or delete their status users.

## /status

This command will simply list the online statuses of every single user that you
have added.

# Notify Commands

## /add_notify_group

This command will allow the user to add a notify group to the current group, so
users in that notify group will be able to notify each other with important
messages

## /modify_notify_group

This requirements of this command has two separate audiences.

### **Group Admins**

Group admins need to have the ability to remove all notify groups that are a
part of the group they administrate, even if they don't own that notify group
However, they should NOT have the ability to modify that notify group

### **Normal Users**

Normal users should be able to edit or delete their notify groups.

## /invite_to_notify_group

Allows Notify Group creators to invite other users to their notify group, and
provide an interface for the invited users to accept/decline the invite.

It also provides an interface for the person who invited (the creator of the 
notify group) to cancel the invitation.

The command also ensures that any person who's being invited is not already a
part of the notify group. If that person is already a part of the notify group,
the creator of the invitation is informed of this in the interface that the
creator uses to cancel invites.


## /list_notify_groups

List all the Notify Groups in a group chat.

## /notify example_notify_group_name optional_message

Notify the users belonging to a notify group with an message provided. 