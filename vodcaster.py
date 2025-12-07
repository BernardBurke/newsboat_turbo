#!/usr/bin/env python3
import sqlite3
import os
import mimetypes
import email.utils
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Schema definition
SCHEMA = """
CREATE TABLE IF NOT EXISTS podcasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    link TEXT,
    base_url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    podcast_id INTEGER,
    title TEXT NOT NULL,
    filename TEXT NOT NULL,
    description TEXT,
    episode_number INTEGER,
    file_size INTEGER,
    mime_type TEXT,
    pub_date TEXT,
    FOREIGN KEY(podcast_id) REFERENCES podcasts(id)
);
"""

ITUNES_NS = 'http://www.itunes.com/dtds/podcast-1.0.dtd'

class VodcastDB:
    def __init__(self, db_path="vodcasts.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def create_podcast(self, title, description, link, base_url):
        # Create a simple slug from title for filenames (e.g., "My Show" -> "my_show")
        slug = "".join(x for x in title if x.isalnum() or x in " -").strip().replace(" ", "_").lower()
        
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO podcasts (title, slug, description, link, base_url)
                VALUES (?, ?, ?, ?, ?)
            """, (title, slug, description, link, base_url))
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            print(f"Error: A podcast with slug '{slug}' already exists.")
            return None

    def get_podcasts(self):
        return self.conn.execute("SELECT * FROM podcasts").fetchall()

    def get_podcast_by_id(self, pid):
        return self.conn.execute("SELECT * FROM podcasts WHERE id = ?", (pid,)).fetchone()

    def add_episode(self, podcast_id, file_path, title, description, episode_num=None):
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'audio/mpeg'

        # Auto-increment episode number if not provided
        if episode_num is None:
            last = self.conn.execute(
                "SELECT MAX(episode_number) as m FROM episodes WHERE podcast_id=?", 
                (podcast_id,)
            ).fetchone()
            episode_num = (last['m'] or 0) + 1

        pub_date = email.utils.formatdate(usegmt=True)

        self.conn.execute("""
            INSERT INTO episodes 
            (podcast_id, title, filename, description, episode_number, file_size, mime_type, pub_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (podcast_id, title, filename, description, episode_num, file_size, mime_type, pub_date))
        self.conn.commit()
        print(f"Episode '{title}' added to database.")

    def generate_rss(self, podcast_id):
        """Generates the physical XML file from the Database"""
        pod = self.get_podcast_by_id(podcast_id)
        if not pod:
            return

        # Setup XML
        ET.register_namespace('itunes', ITUNES_NS)
        root = ET.Element('rss')
        root.set('version', '2.0')
        root.set('xmlns:itunes', ITUNES_NS)
        
        channel = ET.SubElement(root, 'channel')
        ET.SubElement(channel, 'title').text = pod['title']
        ET.SubElement(channel, 'description').text = pod['description']
        ET.SubElement(channel, 'link').text = pod['link'] or pod['base_url']
        
        # Get Episodes sorted by number descending (newest first)
        episodes = self.conn.execute(
            "SELECT * FROM episodes WHERE podcast_id = ? ORDER BY episode_number DESC", 
            (podcast_id,)
        ).fetchall()

        for ep in episodes:
            item = ET.Element('item')
            ET.SubElement(item, 'title').text = ep['title']
            if ep['description']:
                ET.SubElement(item, 'description').text = ep['description']
            
            ET.SubElement(item, 'guid', isPermaLink="false").text = ep['filename']
            ET.SubElement(item, 'pubDate').text = ep['pub_date']
            
            # iTunes specific tags
            if ep['episode_number']:
                # The 'itunes:episode' tag
                ep_elem = ET.SubElement(item, f"{{{ITUNES_NS}}}episode")
                ep_elem.text = str(ep['episode_number'])

            file_url = f"{pod['base_url'].rstrip('/')}/{ep['filename']}"
            ET.SubElement(item, 'enclosure', {
                'url': file_url,
                'length': str(ep['file_size']),
                'type': ep['mime_type']
            })
            
            channel.append(item)

        # Write to file: {slug}.xml
        filename = f"{pod['slug']}.xml"
        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        clean_xml = '\n'.join([line for line in xmlstr.split('\n') if line.strip()])
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(clean_xml)
        print(f"Generated RSS feed: {filename}")
        