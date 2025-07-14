CREATE TABLE chat_message(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chatId INTEGER,
        messageId TEXT,
        parentMessageId TEXT,
        body TEXT,
        createdAt datetime,
        updatedAt datetime,
        FOREIGN KEY (chatId) REFERENCES chat(id)
      );
CREATE TABLE chat(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        model TEXT,
        createdAt datetime,
        updatedAt datetime
      );
