var log_records = [];  // Array of log records returned to Flask
var log_remarks = [];  // Array of remarks to be shown again in the second review

var reviewRemarksRight = {};
var reviewRemarksLeft = {};

$(window).on("load", function(){

    $("#submitter").click(function () {
        logData("pageClosed - fibo1", "pageClosed - fibo1");

        var data = {
            'data': log_records
        }
        var myData = JSON.stringify(data);

        $("#hidden_log").val(myData);

        var string_remarks = JSON.stringify(log_remarks);
        sessionStorage.setItem("remarks", string_remarks);
    });

    $("#submitter2").click(function () {
        logData("pageClosed - fibo2", "pageClosed - fibo2");

        var data = {
            'data': log_records
        }
        var myData = JSON.stringify(data);

        $("#hidden_log2").val(myData);

        var string_remarks = JSON.stringify(log_remarks);
        sessionStorage.setItem("remarks", string_remarks);
    });
});


function checkBox(el) {
    let stringWithoutCommas = el.closest('tr').childNodes[1].innerHTML.trim().replace(/,/g, '');
    logData(stringWithoutCommas,
        `${el.value}`);
}


function retrieveSavedRemarks() {
    var retrieved_remarks = JSON.parse(sessionStorage.getItem("remarks"));
    return retrieved_remarks;
}


function initMergely(elementId, height, contextHeight, width, lineNumberLeft, contentLeft, lineNumberRight, contentRight, prefixLineCount, prefix, suffix) {
    $(elementId).mergely({
        width: width,
        height: height,
        wrap_lines: true,
        fadein: '',
        cmsettings: {
            readOnly: true,
            mode: "text/x-java",
            autoresize: false,
            lineWrapping: true,
            lineNumbers: true,
            foldGutter: true, // Enable fold gutter
            gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter", "remarks"], // Add "CodeMirror-foldgutter"
            extraKeys: {
                "Ctrl-Q": function (cm) {
                    // Keybinding to toggle folding
                    cm.foldCode(cm.getCursor());
                },
            },
        },
        lhs: function(setValue) {
            setValue(contentLeft);
        },
        rhs: function(setValue) {
            setValue(contentRight);
        },
        loaded: function() {
            var el = $(elementId);
            el.mergely('cm', 'lhs').options.firstLineNumber = lineNumberLeft;
            el.mergely('cm', 'rhs').options.firstLineNumber = lineNumberRight;
            el.mergely('cm', 'lhs').on("gutterClick", handleGutterClick);
            el.mergely('cm', 'rhs').on("gutterClick", handleGutterClick);
            el.mergely('cm', 'lhs').hunkId = elementId.replace('#compare', '');
            el.mergely('cm', 'rhs').hunkId = elementId.replace('#compare', '');
            el.mergely('cm', 'lhs').hunkSide = 0;
            el.mergely('cm', 'rhs').hunkSide = 1;
            //store prefix/suffix settings only on the left side
            el.mergely('cm', 'lhs').ps_height = contextHeight;
            el.mergely('cm', 'lhs').ps_linecount = prefixLineCount;
            el.mergely('cm', 'lhs').ps_prefix = prefix;
            el.mergely('cm', 'lhs').ps_lhs = contentLeft;
            el.mergely('cm', 'lhs').ps_rhs = contentRight;
            el.mergely('cm', 'lhs').ps_suffix = suffix;
            el.mergely('cm', 'lhs').ps_prefixActive = false;
            // el.mergely('update', function() {ensureViewCorrectSized(elementId)});
        }
    });
}


function logData(action, data){
    // console.log(`${new Date().getTime()};${action};${data}\n`)
    log_records.push(`${new Date().getTime()};${action};${data}\n`);
}


// function makeMarker(msg) {
// 	var marker = document.createElement("div");
// 	marker.title = msg;
// 	marker.style.color = "#dd0000";
// 	marker.innerHTML = "■";
// 	marker.style.fontSize = "18px";
// 	return marker;
// }

function makeMarker(msg){
    var marker = document.createElement("div");
    var icon = marker.appendChild(document.createElement("span"));
    icon.innerHTML = "!!";
    icon.className = "lint-error-icon";
    var name = marker.appendChild(document.createElement("span"))
    name.innerHTML = "<b>You: </b>";
    marker.appendChild(document.createTextNode(msg));
    marker.className = "lint-error";
    return marker;
}

var instance;
var lineNumber;


function handleGutterClick(instanceTest, lineNumberTest, gutter, clickEvent) {
    // Only process for the line numbers gutter
    if (gutter !== "CodeMirror-linenumbers") return;

    instance = instanceTest;
    lineNumber = lineNumberTest;

    var realLineNumber = lineNumber + instance.options.firstLineNumber;

    if (instance.hunkSide == 1) {
        if (!reviewRemarksRight[instance.hunkId]) {
            reviewRemarksRight[instance.hunkId] = {};
        }

        if (realLineNumber in reviewRemarksRight[instance.hunkId]) {
            prevMsg = reviewRemarksRight[instance.hunkId][realLineNumber].node.lastChild.textContent;
            document.getElementById("review-remark").value = prevMsg;
        }

    } else{
        if (!reviewRemarksLeft[instance.hunkId]) {
            reviewRemarksLeft[instance.hunkId] = {};
        }

        if (realLineNumber in reviewRemarksLeft[instance.hunkId]){
            prevMsg = reviewRemarksLeft[instance.hunkId][realLineNumber].node.lastChild.textContent
            document.getElementById("review-remark").value = prevMsg;
        }
    }

    $("#remark-popup-window").show();
}

function recordRemark() {

    var msg = document.getElementById("review-remark").value;

    document.getElementById("review-remark").value = "";

    var info = instance.lineInfo(lineNumber);
    var prevMsg = "";
    var realLineNumber = lineNumber + instance.options.firstLineNumber;

    if (instance.hunkSide == 1) {
        if (!reviewRemarksRight[instance.hunkId]) {
            reviewRemarksRight[instance.hunkId] = {};
        }

        if (realLineNumber in reviewRemarksRight[instance.hunkId]){
            prevMsg = reviewRemarksRight[instance.hunkId][realLineNumber].node.lastChild.textContent
        }



        if (msg == null) {
            return
        }

        // instance.addLineWidget(lineNumber, makeMarker(msg), {coverGutter: true, noHScroll: true});

        if (realLineNumber in reviewRemarksRight[instance.hunkId]) {
            if (msg == "") {
                // DELETE COMMENT
                logData("deletedComment - intro", `${instance.hunkId}${instance.hunkSide}-${realLineNumber}`);
                reviewRemarksRight[instance.hunkId][realLineNumber].clear()
                // instance.setGutterMarker(lineNumber, "remarks", null);
                delete reviewRemarksRight[instance.hunkId][realLineNumber];
                if(isRemarkPresent(log_remarks, lineNumber, instance.hunkId)) {
                    log_remarks = removeRemark(log_remarks, instance.hunkSide, lineNumber, instance.hunkId);
                }
            } else {
                // UPDATE COMMENT
                logData("updateComment - intro",
                    `${instance.hunkId}${instance.hunkSide}-${realLineNumber}-${msg}`)
                // info.gutterMarkers.remarks.title = msg;
                // reviewRemarksRight[instance.hunkId][realLineNumber] = msg;
                reviewRemarksRight[instance.hunkId][realLineNumber].node.lastChild.textContent = msg
                reviewRemarksRight[instance.hunkId][realLineNumber].changed()
                if(isRemarkPresent(log_remarks, lineNumber, instance.hunkId)) {
                    log_remarks = updateRemark(log_remarks, instance.hunkSide, lineNumber, instance.hunkId, msg);
                }
            }
        } else {
            if (msg == "") {
                // CANCEL COMMENT
                logData("cancelComment - intro",
                    `${instance.hunkId}${instance.hunkSide}-${realLineNumber}`)
            } else {
                // ADD COMMENT
                logData("addComment - intro",
                    `${instance.hunkId}${instance.hunkSide}-${realLineNumber}-${msg}`)
                // instance.setGutterMarker(lineNumber, "remarks", makeMarker(msg));

                var line_widget = instance.addLineWidget(lineNumber, makeMarker(msg), {
                    coverGutter: true,
                    noHScroll: true
                });
                reviewRemarksRight[instance.hunkId][realLineNumber] = line_widget;
                log_remarks.push(new Remark(lineNumber, msg, instance.hunkId, instance.hunkSide));
                // addComment(lineNumber, msg, instance.hunkId, instance.hunkSide)
            }
        }
    } else {
        if (!reviewRemarksLeft[instance.hunkId]) {
            reviewRemarksLeft[instance.hunkId] = {};
        }

        if (realLineNumber in reviewRemarksLeft[instance.hunkId]){
            prevMsg = reviewRemarksLeft[instance.hunkId][realLineNumber].node.lastChild.textContent
        }

        if (msg == null) {
            return
        }

        // instance.addLineWidget(lineNumber, makeMarker(msg), {coverGutter: true, noHScroll: true});

        if (realLineNumber in reviewRemarksLeft[instance.hunkId]) {
            if (msg == "") {
                // DELETE COMMENT
                logData("deletedComment - intro", `${instance.hunkId}${instance.hunkSide}-${realLineNumber}`);
                reviewRemarksLeft[instance.hunkId][realLineNumber].clear()
                // instance.setGutterMarker(lineNumber, "remarks", null);
                delete reviewRemarksLeft[instance.hunkId][realLineNumber];
                if(isRemarkPresent(log_remarks, lineNumber, instance.hunkId)) {
                    log_remarks = removeRemark(log_remarks, instance.hunkSide, lineNumber, instance.hunkId);
                }
            } else {
                // UPDATE COMMENT
                logData("updateComment - intro",
                    `${instance.hunkId}${instance.hunkSide}-${realLineNumber}-${msg}`)
                // info.gutterMarkers.remarks.title = msg;
                // reviewRemarksLeft[instance.hunkId][realLineNumber] = msg;
                reviewRemarksLeft[instance.hunkId][realLineNumber].node.lastChild.textContent = msg
                reviewRemarksLeft[instance.hunkId][realLineNumber].changed()
                if(isRemarkPresent(log_remarks, lineNumber, instance.hunkId)) {
                    log_remarks = updateRemark(log_remarks, instance.hunkSide, lineNumber, instance.hunkId, msg);
                }
            }
        } else {
            if (msg == "") {
                // CANCEL COMMENT
                logData("cancelComment - intro",
                    `${instance.hunkId}${instance.hunkSide}-${realLineNumber}`)
            } else {
                // ADD COMMENT
                logData("addComment - intro",
                    `${instance.hunkId}${instance.hunkSide}-${realLineNumber}-${msg}`)
                // instance.setGutterMarker(lineNumber, "remarks", makeMarker(msg));

                var line_widget = instance.addLineWidget(lineNumber, makeMarker(msg), {coverGutter: true, noHScroll: true});
                reviewRemarksLeft[instance.hunkId][realLineNumber] = line_widget;
                log_remarks.push(new Remark(lineNumber, msg, instance.hunkId, instance.hunkSide));
                // addComment(lineNumber, msg, instance.hunkId, instance.hunkSide)
            }
        }
    }
}

function Remark(line, message, hunk, side) {
    this.line = line;
    this.message = message;
    this.hunk = hunk;
    this.side = side;
}

function isRemarkPresent(remarks_list, line, hunk) {
    for(i = 0; i < remarks_list.length; i++) {
        if(remarks_list[i].hunk == hunk) {
            if(remarks_list[i].line == line) {
                return true;
            }
        }
    }
    return false;
}

function updateRemark(remarks_list, side, line, hunk, message) {
    for(i = 0; i < remarks_list.length; i++) {
        if(remarks_list[i].hunk == hunk && remarks_list[i].side == side) {
            if(remarks_list[i].line == line) {
                remarks_list[i].message = message;
                return remarks_list;
            }
        }
    }
    return null;
}

function removeRemark(remarks_list, side, line, hunk) {
    for(i = 0; i < remarks_list.length; i++) {
        if(remarks_list[i].hunk == hunk && remarks_list[i].side == side) {
            if(remarks_list[i].line == line) {
                remarks_list.splice(i, 1);
                return remarks_list;
            }
        }
    }
    return null;
}

function addToCurrentRemarks(old_remark_widget, old_remark_line, instance) {
    var real_line = old_remark_line + instance.options.firstLineNumber;
    if (!reviewRemarksRight[instance.hunkId]) {
        reviewRemarksRight[instance.hunkId] = {};
    }
    reviewRemarksRight[instance.hunkId][real_line] = old_remark_widget;
}


function promptPromise(message) {
    var dialog       = document.getElementById('dialog');
    var input        = dialog.querySelector('input');
    var okButton     = dialog.querySelector('button.ok');
    var cancelButton = dialog.querySelector('button.cancel');

    dialog.querySelector('.message').innerHTML = String(message);
    dialog.className = '';

    return new Promise(function(resolve, reject) {
        dialog.addEventListener('click', function handleButtonClicks(e) {
            if (e.target.tagName !== 'BUTTON') { return; }
            dialog.removeEventListener('click', handleButtonClicks);
            dialog.className = 'hidden';
            if (e.target === okButton) {
                resolve(input.value);
            } else {
                reject(new Error('User cancelled'));
            }
        });
    });
}

