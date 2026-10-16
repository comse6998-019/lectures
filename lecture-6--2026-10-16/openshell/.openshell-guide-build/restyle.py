from pathlib import Path
import re
p=Path('.openshell-guide-build/template.html')
s=p.read_text()
script=s.split('<script>',1)[1].split('</script>',1)[0]
start=script.index("  const key=")
end=script.index('  let detailsBeforePrint=')
script=script[:start]+"  const chapters=Array.from(document.querySelectorAll('.chapter'));\n"+script[end:]
start=script.index('  const navLinks=')
end=script.index('  const flow=',start)
script=script[:start]+script[end:]
script=script.replace("const box=document.getElementById('sim-result');", "const box=document.getElementById('sim-result');")
css='''
:root{color-scheme:light}
body{margin:8px;background:white;color:black;font-family:"Times New Roman",Times,serif;font-size:16px;line-height:normal}
a:link{color:#0000ee}a:visited{color:#551a8b}a:hover{text-decoration:underline}a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:2px solid #0f62fe;outline-offset:3px}
[hidden]{display:none!important}.skip{position:absolute;left:-10000px}.skip:focus{left:8px;top:8px;background:white;padding:8px}
.document-title{text-align:center}.document-title h1{font-size:2em}.document-title h3{font-size:1.17em}
.contents ol{list-style:none;padding:0;margin:0}.contents ol ol{padding-left:1em}.contents li{margin:0}.contents h1{font-size:2em}.section-number{margin-right:.45em}
.page-tools{margin:1em 0}.text-button{appearance:none;background:none;border:0;border-radius:0;padding:0;font:inherit;color:#0000ee;text-decoration:underline;cursor:pointer}
.intro{margin:1em 0}.study-routes p{margin:.6em 0}.chapter{margin-top:1.5em}.chapter h2{font-size:1.5em}.chapter h3{font-size:1.17em}.chapter h4{font-size:1em}.chapter-head .lead{font-style:normal}.chapter-return{font-size:small;text-align:right}.eyebrow,.chapter-meter{display:none}
.table-wrap{max-width:100%;overflow-x:auto;margin:1em 0}table{border-collapse:collapse;width:100%}th,td{border:1px solid #aaa;padding:6px 8px;text-align:left;vertical-align:top}th{font-weight:bold;background:white}td{overflow-wrap:anywhere}
code,pre{font-family:monospace;font-size:.85em}code{overflow-wrap:anywhere}pre{font-size:13px;line-height:1.35;overflow:auto;max-width:100%;margin:1em 0;padding:8px;background:#f8f8f8;border:1px solid #ddd;tab-size:2}pre code{font-size:inherit;white-space:pre;overflow-wrap:normal}.code-wrap{position:relative}.copy-code{display:block;margin:-.6em 0 1em auto;font-size:11px}
.callout{margin:1em 2em}.callout p{margin:.6em 0}.sources{font-size:1em}.exercise{margin:1em 0}.exercise summary{font-weight:bold;cursor:pointer}.exercise>p,.exercise>ol{margin-left:1.5em}.paired{display:flex;gap:2em}.paired>div{flex:1;min-width:0}.glossary dt{font-weight:bold;margin-top:1em}.glossary dd{margin-top:.25em}.footnote{font-size:small}.source-ledger{list-style:none;counter-reset:reference;padding-left:3em}.source-ledger li{counter-increment:reference;position:relative;margin:1em 0;overflow-wrap:anywhere}.source-ledger li::before{content:"[" counter(reference) "]";position:absolute;right:calc(100% + .5em)}footer{margin-top:2em;font-size:small}
.tikz-figure{margin:1.5em 0;text-align:center}.diagram-scroll{overflow-x:auto;max-width:100%}.tikz-figure img{display:block;margin:0 auto;max-width:100%;height:auto}.tikz-figure figcaption{max-width:75em;margin:.6em auto 0;text-align:left}.figure-source{font-size:small;margin:.4em 0}.diagram-transcript{font-size:small;text-align:left}.diagram-transcript summary{cursor:pointer}.diagram-transcript ol{margin:.5em 0}
.interactive{border:1px solid #aaa;padding:1em;margin:1em 0;max-width:65em}.widget-heading{display:flex;justify-content:space-between;gap:1em}.flow-track{display:flex;list-style:none;padding:0;gap:1em;flex-wrap:wrap}.flow-track li.active{font-weight:bold;text-decoration:underline}#flow-detail{min-height:5em}.widget-actions{display:flex;justify-content:space-between}.control-grid{display:grid;grid-template-columns:1fr 1fr;gap:.75em 1em;margin:1em 0}.control-grid label{display:flex;flex-direction:column;gap:.25em}.control-grid select{max-width:100%;min-width:0;padding:3px}.sim-result{border-top:1px solid #aaa;padding-top:.75em}.sim-result p{margin:.5em 0}.sim-result.denied strong{color:#800000}
button{cursor:pointer}button:disabled{cursor:default}dialog{color:black;background:white;width:min(700px,calc(100% - 50px));max-height:80vh;padding:20px;border:1px solid #555}dialog::backdrop{background:#0006}.search-head{display:flex;align-items:center;justify-content:space-between;gap:1em}.search-head h2{margin-top:0}#search-input{box-sizing:border-box;width:100%;font-size:16px}#search-results{list-style:none;padding:0;max-height:45vh;overflow:auto}#search-results li{margin:1em 0}#search-results strong,#search-results span{display:block}#search-results span{color:black;margin-top:.25em}.search-hit{background:#ffffcc}
@media(max-width:600px){.paired{display:block}.control-grid{grid-template-columns:1fr}.control-grid select{font-size:16px}.callout{margin:1em}.widget-heading{display:block}.widget-heading span{display:block;margin-top:.5em}.tikz-figure img{max-width:none;min-width:0}.tikz-figure figcaption{font-size:small}.table-wrap table{font-size:14px}}
@page{size:A4;margin:16mm}
@media print{body{margin:0;font-size:10pt}.page-tools,.copy-code,.chapter-return,.widget-actions,.control-grid,dialog,.figure-source{display:none!important}h1,h2,h3,h4{break-after:avoid}.chapter{break-before:page}.chapter p{orphans:3;widows:3}.tikz-figure,.exercise{break-inside:avoid}.tikz-figure img{max-width:100%;width:auto!important;max-height:220mm}.diagram-scroll,.table-wrap{overflow:visible}.table-wrap{font-size:9pt}tr{break-inside:avoid}thead{display:table-header-group}pre,pre code{white-space:pre-wrap;overflow-wrap:anywhere}pre{overflow:visible;font-size:8pt}a:link,a:visited{color:#0000ee}.diagram-transcript{display:none}footer{font-size:8pt}}
'''
header='''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="description" content="An account of OpenShell: process isolation, runtime mediation, policy, credentials, distributed state, and formal policy analysis.">
<title>OpenShell: Architecture, Enforcement, and Policy</title>
<style>'''+css+'''</style>
</head>
<body>
<a class="skip" href="#main">Skip to the text</a>
<header class="document-title" id="top"><h1>OpenShell</h1><h3>Architecture, Enforcement, and Policy</h3><h3>Last update: October 6, 2026</h3></header>
<hr>
<nav class="contents" aria-label="Contents" id="contents"><h1>Contents</h1>{{NAV}}</nav>
<p class="page-tools"><button class="text-button" id="open-search" type="button">Search this document</button> &middot; <button class="text-button" id="print" type="button">Print</button></p>
<hr>
<main id="main">
<div class="intro"><p>OpenShell controls the authority available to programs running in a sandbox. This account begins with processes and operating-system isolation, then examines the mechanisms that govern network access, provider credentials, policy changes, and resource management.</p>
<p>The central distinction is between a requested action and the authority to perform it. A model may select an action; an ordinary process executes it; the runtime and operating system enforce the relevant restrictions. The account follows these responsibilities through the source code.</p>
<p>Sections 1–3 establish the concepts and component boundaries. Sections 4–6 describe management and deployment. Sections 7–12 examine runtime enforcement, credentials, and policy analysis. Sections 13–16 cover clients, diagnosis, experiments, and exercises. Sections 17–18 provide a glossary and repository map.</p>
<p>This edition describes commit <code>be7af99ff2eacba807d82b69adb0c3d4eaa32158</code>, studied on October 5, 2026. Source references identify that revision. The HTML includes its figures and interactive examples; only external source links require a network connection.</p></div>
{{CONTENT}}
<footer><hr><p>Source edition: <code>be7af99ff2eacba807d82b69adb0c3d4eaa32158</code>. Source study: October 5, 2026. Text and presentation revised: October 6, 2026.</p><p>The account is based on the local source checkout. Runtime experiments are supplied for practice and were not executed during the source study.</p></footer>
</main>
<dialog id="search-dialog" aria-labelledby="search-title"><div class="search-head"><h2 id="search-title">Search the document</h2><button type="button" id="close-search" aria-label="Close search">Close</button></div><label for="search-input">Concept, component, command, or source path</label><input id="search-input" type="search" placeholder="credential, readiness, seccomp…" autocomplete="off"><p id="search-status" aria-live="polite">Type at least two characters.</p><ul id="search-results"></ul></dialog>
'''
p.write_text(header+'<script>'+script+'</script>\n</body>\n</html>\n')
