# Purpose
The backfill directory is designed to load old emails into the MX (AKA backfill). These emails will be processed by Sage as though they were forwarded from the forwarding email. 

# Requirements
- TODO: Add requirements; how does Sage know to process these emails even though they weren't forwarded?

# Instructions
1. Create a `real_data/` directory in `backfill/`. `real_data/` is already in `.gitignore`, but be careful not to accidentally commit it. 
2. Move the .mbox file to `backfill/readl_data`.