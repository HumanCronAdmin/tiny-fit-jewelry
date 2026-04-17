Tiny Fit Newsletter System
=========================

How it works:
1. Write your email as a draft / .txt file
2. Format: first line = subject, blank line, body (Markdown OK)
3. Run: python scripts/newsletter_send.py --preview
   -> preview exactly what will be sent
Run: python scripts/newsletter_send.py --send
   -> actually send to all subscribers

Nothing is sent automatically. You always decide when to send.

Folder Structure
  draft/ <- put new mail here
  sent/ <- move here after sending (automatically)

Example of a draft file (drafts/002_new_brands.txt):

  Three brands we haven't tried yet

  Hello,

  I found 3 brands this month that actually carry 2-3 size rings.

  (Continued from body of email)