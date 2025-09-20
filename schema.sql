BEGIN;

CREATE TABLE IF NOT EXISTS Errors (
    id SERIAL PRIMARY KEY,
    command TEXT NOT NULL,
    user_id BIGINT NOT NULL,
    guild BIGINT,
    error TEXT NOT NULL,
    full_error TEXT NOT NULL,
    message_url TEXT NOT NULL,
    occured_when TIMESTAMP NOT NULL,
    fixed BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS ErrorReminders (
    id BIGINT references Errors (id),
    user_id BIGINT NOT NULL,
    PRIMARY KEY (id, user_id)
);

CREATE TABLE IF NOT EXISTS Feature (
    feature_type FeatureTypes NOT NULL,
    user_id BIGINT,
    guild_id BIGINT,
    allowed BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS Timers (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    reserved_type INTEGER,
    expires TIMESTAMP WITH TIME ZONE NOT NULL,
    data JSONB
);

COMMIT;

-- The tables above are for the bot base. They help the bot run its internals
-- The tables below are solely for Anicord Gacha.
BEGIN;

CREATE TABLE IF NOT EXISTS Cards (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    rarity INTEGER NOT NULL,
    theme TEXT NOT NULL references Themes (name),
    -- Basic properties
    is_obtainable BOOLEAN DEFAULT true,
    -- Image proprties
    -- Temporarily, some data
    image_url TEXT NOT NULL,
    -- #TODO: Add image based columns when the initial image storage is provided
    -- Misc
    notes TEXT
);

CREATE TABLE IF NOT EXISTS Themes (
    name TEXT PRIMARY KEY,
    is_disabled BOOLEAN DEFAULT false
);

CREATE TABLE IF NOT EXISTS CardInventory (
    user_id BIGINT NOT NULL,
    id INTEGER NOT NULL references Cards (id),
    quantity INTEGER NOT NULL,
    is_locked BOOLEAN DEFAULT false,
    -- Shop
    shop_listing_id INTEGER,
    -- Misc
    notes TEXT,
    PRIMARY KEY (user_id, id)
);

CREATE TABLE IF NOT EXISTS CardInventoryNotes (
    user_id BIGINT NOT NULL,
    id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (user_id, id, tag)
);

CREATE TABLE IF NOT EXISTS PlayerData (
    user_id BIGINT PRIMARY KEY,
    blombos INTEGER DEFAULT 0,
    bio TEXT,
    wallpaper INTEGER references CardInventory (id)
);

CREATE TABLE IF NOT EXISTS PullIntervals (
    user_id BIGINT NOT NULL references PlayerData (user_id),
    theme TEXT NOT NULL references Themes (name),
    last_pull TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (user_id, theme)
);

COMMIT;
