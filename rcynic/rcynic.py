"""
Python translation of rcynic.xsl, which has gotten too slow and complex.

$Id$

Copyright (C) 2010-2011 Internet Systems Consortium, Inc. ("ISC")

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND ISC DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS.  IN NO EVENT SHALL ISC BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
"""

import sys, urlparse, os

from xml.etree.ElementTree import (ElementTree, Element, SubElement, Comment)

refresh = 1800
suppress_zero_columns = True
show_total = True
use_colors = True
show_detailed_status = True
show_problems = False
show_summary = True

class Label(object):

  def __init__(self, elt):
    self.code = elt.tag
    self.mood = elt.get("kind")
    self.text = elt.text.strip()
    self.sum  = 0

class Validation_Status(object):

  def __init__(self, elt, map):
    self.uri = elt.text.strip()
    self.timestamp = elt.get("timestamp")
    self.generation = elt.get("generation")
    self.hostname = urlparse.urlparse(self.uri).hostname or None
    self.fn2 = os.path.splitext(self.uri)[1] or None if self.generation else None
    self.label = map[elt.get("status")]
    self.label.sum += 1

  @property
  def code(self):
    return self.label.code

  @property
  def mood(self):
    return self.label.mood

input = ElementTree(file = sys.stdin)
labels = [Label(elt) for elt in input.find("labels")]
label_map = dict((l.code, l) for l in labels)
validation_status = [Validation_Status(elt, label_map) for elt in input.findall("validation_status")]
del label_map
if suppress_zero_columns:
  labels = [l for l in labels if l.sum > 0]

html = Element("html")
html.append(Comment(" Generators:\n" +
                    "  " + input.getroot().get("rcynic-version") + "\n" +
                    "  $Id$\n"))
head = SubElement(html, "head")
body = SubElement(html, "body")

title = "rcynic summary %s" % input.getroot().get("date")
SubElement(head, "title").text = title
SubElement(body, "h1").text = title
del title

if refresh:
  SubElement(head, "meta", { "http-equiv" : "Refresh", "content" : str(refresh) })

SubElement(head, "style", type = "text/css").text = '''
  th, td          { text-align: center; padding: 4px }
  td.uri          { text-align: left }
  thead tr th,
  tfoot tr td     { font-weight: bold }
'''

table_css = { "rules" : "all", "border" : "1"}
uri_css   = { "class" : "uri" }

if use_colors:
  SubElement(head, "style", type = "text/css").text = '''
  .good           { background-color: #77ff77 }
  .warn           { background-color: yellow }
  .bad            { background-color: #ff5500 }
'''

if show_summary:

  unique_hostnames   = sorted(set(v.hostname   for v in validation_status))
  unique_fn2s        = sorted(set(v.fn2        for v in validation_status))
  unique_generations = sorted(set(v.generation for v in validation_status))

  if show_summary:

    SubElement(body, "br")
    SubElement(body, "h2").text = "Grand Totals"
    table = SubElement(body, "table", table_css)
    thead = SubElement(table, "thead")
    tfoot = SubElement(table, "tfoot")
    tbody = SubElement(table, "tbody")
    tr = SubElement(thead, "tr")
    SubElement(tr, "th")
    for l in labels:
      SubElement(tr, "th").text = l.text
    for fn2 in unique_fn2s:
      for generation in unique_generations:
        if any(v.fn2 == fn2 and v.generation == generation for v in validation_status):
          tr = SubElement(tbody, "tr")
          SubElement(tr, "td").text = ((generation or "") + " " + (fn2 or "")).strip()
          for l in labels:
            value = sum(int(v.fn2 == fn2 and v.generation == generation and v.code == l.code) for v in validation_status)
            td = SubElement(tr, "td")
            if value > 0:
              td.set("class", l.mood)
              td.text = str(value)

    tr = SubElement(tfoot, "tr")
    SubElement(tr, "td").text = "Total"
    for l in labels:
      SubElement(tr, "td", { "class" : l.mood }).text = str(l.sum)
    
    SubElement(body, "br")
    SubElement(body, "h2").text = "Summaries by Repository Host"
    for hostname in unique_hostnames:
      SubElement(body, "br")
      SubElement(body, "h3").text = hostname
      table = SubElement(body, "table", table_css)
      thead = SubElement(table, "thead")
      tfoot = SubElement(table, "tfoot")
      tbody = SubElement(table, "tbody")
      tr = SubElement(thead, "tr")
      SubElement(tr, "th")
      for l in labels:
        SubElement(tr, "th").text = l.text
      for fn2 in unique_fn2s:
        for generation in unique_generations:
          if any(v.hostname == hostname and v.fn2 == fn2 and v.generation == generation for v in validation_status):
            tr = SubElement(tbody, "tr")
            SubElement(tr, "td").text = ((generation or "") + " " + (fn2 or "")).strip()
            for l in labels:
              value = sum(int(v.hostname == hostname and v.fn2 == fn2 and v.generation == generation and v.code == l.code) for v in validation_status)
              td = SubElement(tr, "td")
              if value > 0:
                td.set("class", l.mood)
                td.text = str(value)

      tr = SubElement(tfoot, "tr")
      SubElement(tr, "td").text = "Total"
      for l in labels:
        value = sum(int(v.hostname == hostname and v.code == l.code) for v in validation_status)
        td = SubElement(tr, "td")
        if value > 0:
          td.set("class", l.mood)
          td.text = str(value)

  if show_problems:

    SubElement(body, "br")
    SubElement(body, "h2").text = "Problems"
    table = SubElement(body, "table", table_css)
    thead = SubElement(table, "thead")
    tbody = SubElement(table, "tbody")
    tr = SubElement(thead, "tr")
    SubElement(tr, "th").text = "Status"
    SubElement(tr, "th").text = "URI"
    for v in validation_status:
      if v.mood != "good":
        tr = SubElement(tbody, "tr", { "class" : v.mood })
        SubElement(tr, "td").text = v.label.text
        SubElement(tr, "td", uri_css).text = v.uri
  
  if show_detailed_status:

    SubElement(body, "br")
    SubElement(body, "h2").text = "Validation Status"
    table = SubElement(body, "table", table_css)
    thead = SubElement(table, "thead")
    tbody = SubElement(table, "tbody")
    tr = SubElement(thead, "tr")
    SubElement(tr, "th").text = "Timestamp"
    SubElement(tr, "th").text = "Generation"
    SubElement(tr, "th").text = "Status"
    SubElement(tr, "th").text = "URI"
    for v in validation_status:
      tr = SubElement(tbody, "tr", { "class" : v.mood })
      SubElement(tr, "td").text = v.timestamp
      SubElement(tr, "td").text = v.generation
      SubElement(tr, "td").text = v.label.text
      SubElement(tr, "td", uri_css).text = v.uri

ElementTree(element = html).write(sys.stdout)
