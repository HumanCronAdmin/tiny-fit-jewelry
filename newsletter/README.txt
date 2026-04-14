TinyFit Newsletter System
=========================

How it works:
1. Write an email in drafts/ as a .txt file
2. Format: first line = subject, blank line, then body (Markdown OK)
3. Run: python scripts/newsletter_send.py --preview
   -> Shows you exactly what will be sent
4. Run: python scripts/newsletter_send.py --send
   -> Actually sends to all subscribers

Nothing sends automatically. You always decide when.

Folder structure:
  drafts/       <- Put new emails here
  sent/         <- Emails move here after sending (auto)

Example draft file (drafts/002_new_brands.txt):

  Three brands you probably haven't tried yet

  Hey,

  I found three brands this month that actually carry ring sizes 2-3...

  (rest of email body)
