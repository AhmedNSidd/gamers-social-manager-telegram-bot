CREATE TABLE IF NOT EXISTS StatusUsers (
    id SERIAL PRIMARY KEY,
    telegramChatID BIGINT,
    telegramUserID BIGINT,
    displayName TEXT,
    xboxGamertag TEXT,
    xboxAccountID BIGINT,
    psnOnlineID TEXT,
    psnAccountID BIGINT
);

CREATE TABLE IF NOT EXISTS NotifyGroups (
    id SERIAL PRIMARY KEY,
    telegramChatID BIGINT,
    creatorID BIGINT,
    name TEXT,
    description TEXT,
    inviteOnly BOOLEAN,
    members BIGINT[],
    invited TEXT[]
);

CREATE TABLE IF NOT EXISTS Credentials (
    id INT NOT NULL UNIQUE DEFAULT 1 CHECK (id = 1),
    xboxClientID TEXT,
    xboxClientSecret TEXT,
    xboxTokenType TEXT,
    xboxExpiresIn INT,
    xboxScope TEXT,
    xboxAccessToken TEXT,
    xboxRefreshToken TEXT,
    xboxUserID TEXT,
    xboxIssued TEXT, 
    psnNpsso TEXT
);

INSERT INTO Credentials VALUES (1) ON CONFLICT DO NOTHING;