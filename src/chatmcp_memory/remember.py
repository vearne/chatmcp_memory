import logging

from pydantic import Field
from typing import Annotated
from enum import Enum
import platform
import os
import sys
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta
import json

from .dto import Chat, ChatMessage


class OS(str, Enum):
    ANDROID = 'Android'
    IOS = 'iOS'
    MACOS = 'macOS'
    WINDOWS = 'Windows'
    UNKNOWN = 'Unknown'


def detect_os() -> OS:
    """
    Detect the current operating system.

    Returns:
        OS: Enum member representing the detected OS.
    """
    system = platform.system()

    if system == 'Windows':
        return OS.WINDOWS

    # Detect Android via environment variables commonly set in Android Python environments
    if 'ANDROID_ARGUMENT' in os.environ or 'ANDROID_ROOT' in os.environ:
        return OS.ANDROID

    # Detect iOS via sys.platform
    if sys.platform == 'ios':
        return OS.IOS

    if system == 'Darwin':
        return OS.MACOS

    return OS.UNKNOWN

def get_db_path() -> str:
    """
        Retrieve the file path of SQLite database(chatmcp.db)
        https://github.com/daodao97/chatmcp/blob/main/lib/utils/storage_manager.dart
    """
    value = os.getenv('DB_FILE_PATH')
    if value is not None:
        return value

    _appName = 'ChatMcp'

    os_type = detect_os()
    if os_type == OS.WINDOWS:
        data_path = os.getenv('APPDATA')
        if data_path is None:
            # Fallback to user home directory if APPDATA is not set
            data_path = os.path.expanduser('~')
        app_data_path = os.path.join(data_path, _appName)
    elif os_type == OS.ANDROID:
        # On Android, use the environment variable ANDROID_DATA or fallback to /data/data/<package>
        android_data = os.getenv('ANDROID_DATA')
        if android_data:
            app_data_path = os.path.join(android_data, _appName)
        else:
            # Fallback path, may need adjustment depending on app packaging
            app_data_path = f'/data/data/{_appName}'
    elif os_type == OS.IOS:
        # On iOS, use HOME directory and Documents folder
        home_dir = os.getenv('HOME')
        if home_dir is None:
            home_dir = os.path.expanduser('~')
        app_data_path = os.path.join(home_dir, 'Documents', _appName)
    elif os_type == OS.MACOS:
        home_dir = os.getenv("HOME")
        if home_dir is None:
            home_dir = os.path.expanduser('~')
        app_data_path = os.path.join(home_dir, 'Library', 'Application Support', _appName)
    else:
        return "unknown"

    db_path = os.path.join(app_data_path, 'chatmcp.db')
    return db_path


def remember(
        keyword: Annotated[str, Field(description="key word")],
        start_date: Annotated[str, Field(
            description="Start date in 'YYYYMMDD' format (e.g. '20250620'). When empty, automatically uses the date 3 months before today")],
        end_date: Annotated[str, Field(
            description="End date in 'YYYYMMDD' format (e.g. '20250703'). When empty, automatically uses today's date")],
        max_message_count: Annotated[
            int | None, Field(description="The maximum number of messages that can be returned, default: 200", ge=1)
        ] = 200,
) -> str:
    """
        Retrieve historical chat records between users and LLM
    """

    if start_date is "":
        start = datetime.now() + timedelta(days=-90)
    else:
        start = datetime.strptime(start_date, '%Y%m%d')

    if end_date is "":
        end = datetime.now() + timedelta(days=1)
    else:
        end = datetime.strptime(end_date, '%Y%m%d')

    # SQLite has no notion of time zones; to accommodate them, add one day to end.
    end = end + timedelta(days=1)

    db_path = get_db_path()
    logging.info("db_path:%s", db_path)
    if not os.path.exists(db_path):
        return f"File does not exist: {db_path}"

    sql = """
    SELECT c.id,
           c.model,
           c.title,
           c.createdAt as chatCreatedAt,
           m.chatId,
           m.messageId,
           m.parentMessageId,
           m.body,
           m.createdAt
    FROM chat AS c
    JOIN chat_message AS m
          ON c.id = m.chatId
    WHERE m.body LIKE ? AND m.createdAt BETWEEN ? AND ?
    ORDER BY m.id DESC LIMIT ?;
    """
    pattern = f'%{keyword}%'
    logging.info("query params: %s", (pattern, start, end, max_message_count))
    with sqlite3.connect(db_path) as conn:
        record_list = fetch_dict(conn, sql, (pattern, start, end, max_message_count))

    # order by time (ascending)
    record_list.reverse()
    logging.info("get chatMessage: %d", len(record_list))

    session_map = {}
    for record in record_list:
        chat_id = record["chatId"]
        if not chat_id in session_map:
            c = Chat()
            c.chat_id = int(chat_id)
            c.title = record["title"]
            c.model = record["model"]
            c.created_at = record["chatCreatedAt"]
            c.messages = []
            session_map[chat_id] = c

        msg = ChatMessage()
        msg.message_id = record["messageId"]
        msg.parent_message_id = record["parentMessageId"]
        msg.body = record["body"]
        msg.created_at = record["createdAt"]
        session_map[chat_id].messages.append(msg)

    result = []
    for record in record_list:
        chat_id = record["chatId"]
        if chat_id in session_map:
            result.append(session_map.pop(chat_id).model_dump())

    logging.info("get chat: %d", len(result))
    return json.dumps({"result":result})

# convert to dictionary format
def fetch_dict(conn, sql, params=()):
    conn.row_factory = sqlite3.Row
    with closing(conn.cursor()) as cur:
        cur.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]

