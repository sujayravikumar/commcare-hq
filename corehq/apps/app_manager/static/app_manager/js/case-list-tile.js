function CaseListTile(options) {
    var o = {
        unit: options.unit || 40
    };
    var u = o.unit;
    var tileWidth = 12;
    var tileHeight = 4;
    var self = {};
    self.$canvasGroup = $('<div/>').css({position: 'relative', width: tileWidth * u, height: tileHeight * u}).disableSelection();
    var $canvas = $('<canvas width="' + tileWidth * u + '" height="' + tileHeight * u + '"></canvas>')
        .css({
            border: '1px solid #EEEEEE',
            position: 'absolute',
            left: 0,
            top: 0,
            zIndex: 0
        })
        .appendTo(self.$canvasGroup);
    var $affordanceCanvas = $('<canvas width="' + tileWidth * u + '" height="' + tileHeight * u + '" tabindex="-1"></canvas>')
        .css({
            position: 'absolute',
            left: 0,
            top: 0,
            zIndex: 1
        })
        .appendTo(self.$canvasGroup);
    var context = $canvas.get(0).getContext("2d");
    var affordanceContext = $affordanceCanvas.get(0).getContext("2d");
    self.boxes = ko.observableArray();
    self.selectedBox = ko.observable(null);
    self.affordanceBoxes = ko.observableArray();
    var getCursorPositionPx = function (e) {
        /* get pixel position from top left of canvas */
        var x;
        var y;
        if (e.pageX != undefined && e.pageY != undefined) {
            x = e.pageX;
            y = e.pageY;
        }
        else {
            x = e.clientX + document.body.scrollLeft + document.documentElement.scrollLeft;
            y = e.clientY + document.body.scrollTop + document.documentElement.scrollTop;
        }
        x -= self.$canvasGroup.get(0).offsetLeft;
        y -= self.$canvasGroup.get(0).offsetTop;
        return {
            x: x,
            y: y
        };
    };
    var getCursorPosition = function (e) {
        /* get quantized box position from top left of canvas */
        var px = getCursorPositionPx(e);
        return {
            i: Math.floor(px.x/u),
            j: Math.floor(px.y/u)
        };
    };
    var getClosestVertex = function (px) {
        /* take a pixel location and round to the nearest vertext */
        return {
            i: Math.floor((px.x)/u +.5),
            j: Math.floor((px.y)/u +.5)
        };
    };
    var boxUnderCursorPosition = function (loc, boxesArray) {
        /* boxesArray is a dumb array, not ko.ObservableArray */

        for (var a = 0; a < boxesArray.length; a++) {
            var box = boxesArray[a];
            if (box.i() <= loc.i && loc.i < box.i() + box.width() &&
                box.j() <= loc.j && loc.j < box.j() + box.height()) {
                return box;
            }
        }
        return null;
    };
    var edgeUnderCursorPosition = function (locPx, boxesArray) {
        var fudge = 2;
        for (var a = 0; a < boxesArray.length; a++) {
            var box = boxesArray[a];
            if (box.i() * u - fudge <= locPx.x && locPx.x < (box.i() + box.width()) * u + fudge &&
                box.j() * u - fudge <= locPx.y && locPx.y < (box.j() + box.height()) * u + fudge) {
                var match = {
                    box: box,
                    top: Math.abs(locPx.y - box.j() * u) < fudge,
                    right: Math.abs(locPx.x - (box.i() + box.width()) * u) < fudge,
                    bottom: Math.abs(locPx.y - (box.j() + box.height()) * u) < fudge,
                    left: Math.abs(locPx.x - box.i() * u) < fudge
                };
                if (match.top || match.right || match.bottom || match.left) {
                    return match;
                }
            }
        }
        return null;
    };
    var getTransposedBox = function (box, selection) {
        var xMove = selection.end.i - selection.start.i;
        var yMove = selection.end.j - selection.start.j;
        var newI = box.i() + xMove;
        var newJ = box.j() + yMove;
        if (newI < 0) {
            newI = 0;
        }
        if (newJ < 0) {
            newJ = 0;
        }
        if (newI + box.width() >= tileWidth) {
            newI = tileWidth - box.width();
        }
        if (newJ + box.height() >= tileHeight) {
            newJ = tileHeight - box.height();
        }
        return {
            i: newI,
            j: newJ
        };
    };
    var getBoxFromSelection = function (selection) {
        var normalizedSelection = {
            start: {
                i: selection.start.i <= selection.end.i ? selection.start.i : selection.end.i,
                j: selection.start.j <= selection.end.j ? selection.start.j : selection.end.j
            },
            end: {
                i: selection.start.i <= selection.end.i ? selection.end.i : selection.start.i,
                j: selection.start.j <= selection.end.j ? selection.end.j : selection.start.j
            }
        };
        return {
            i: normalizedSelection.start.i,
            j: normalizedSelection.start.j,
            width: normalizedSelection.end.i - normalizedSelection.start.i + 1,
            height: normalizedSelection.end.j - normalizedSelection.start.j + 1
        };
    };
    var getResizedBox = function (match, endVertex) {
        var box = match.box;
        var newBox = {
            i: box.i(),
            j: box.j(),
            width: box.width(),
            height: box.height()
        };
        if (match.top) {
            if (endVertex.j >= box.j() + box.height()) {
                newBox.height = 1;
                newBox.j = box.j() + box.height() - 1;
            } else {
                newBox.height = box.height() - (endVertex.j - box.j());
                newBox.j = endVertex.j;
            }
        }
        if (match.bottom) {
            if (endVertex.j - box.j() <= 0) {
                newBox.height = 1;
            } else {
                newBox.height = endVertex.j - box.j();
            }
        }
        if (match.left) {
            if (endVertex.i >= box.i() + box.width()) {
                newBox.height = 1;
                newBox.i = box.i() + box.width() - 1;
            } else {
                newBox.width = box.width() - (endVertex.i - box.i());
                newBox.i = endVertex.i;
            }
        }
        if (match.right) {
            if (endVertex.i - box.i() <= 0) {
                newBox.width = 1;
            } else {
                newBox.width = endVertex.i - box.i();
            }
        }
        return newBox;
    };
    var selection = null;
    $affordanceCanvas.mousedown(function (e) {
        if (selection) {
            // user started a selection and mouseup'd outside the canvas
            // and is re-clicking to finish selection
            // which will happen in mouseup
            return;
        }
        selection = {};
        selection.start = getCursorPosition(e);
        selection.startPx = getCursorPositionPx(e);
        var edgeMatch = edgeUnderCursorPosition(selection.startPx, self.boxes());
        var box = boxUnderCursorPosition(selection.start, self.boxes());
        if (edgeMatch) {
            selection.isDrag = false;
            selection.dragBox = null;
            selection.isResize = true;
            selection.resizeMatch = edgeMatch;
        } else if (box) {
            selection.isDrag = true;
            selection.dragBox = box;
            selection.isResize = false;
            selection.resizeMatch = null;
        } else {
            selection.isDrag = false;
            selection.dragBox = null;
            selection.isResize = false;
            selection.resizeMatch = null;
        }
    });
    $affordanceCanvas.mousemove(function (e) {
        var loc = getCursorPosition(e);
        var locPx = getCursorPositionPx(e);
        if (selection) {
            var affordanceSelection = {
                start: {i: selection.start.i, j: selection.start.j},
                end: loc
            };
            if (selection.isResize) {
                var boxDimensions = getResizedBox(selection.resizeMatch, getClosestVertex(locPx));
                self.affordanceBoxes.splice(0, self.affordanceBoxes().length, {
                    i: ko.observable(boxDimensions.i),
                    j: ko.observable(boxDimensions.j),
                    width: ko.observable(boxDimensions.width),
                    height: ko.observable(boxDimensions.height)
                });
            } else if (selection.isDrag) {
                var newPosition = getTransposedBox(selection.dragBox, affordanceSelection);
                self.affordanceBoxes.splice(0, self.affordanceBoxes().length, {
                    i: ko.observable(newPosition.i),
                    j: ko.observable(newPosition.j),
                    width: ko.observable(selection.dragBox.width()),
                    height: ko.observable(selection.dragBox.height())
                });
            } else {
                var boxDimensions = getBoxFromSelection(affordanceSelection);
                self.affordanceBoxes.splice(0, self.affordanceBoxes().length, {
                    i: ko.observable(boxDimensions.i),
                    j: ko.observable(boxDimensions.j),
                    width: ko.observable(boxDimensions.width),
                    height: ko.observable(boxDimensions.height)
                });
            }
        } else {
            var match = null;
            if (match = edgeUnderCursorPosition(locPx, self.boxes())) {
                e.target.style.cursor = (function () {
                    if (match.top && match.right || match.bottom && match.left) {
                        return 'nesw-resize';
                    }
                    if (match.top && match.left || match.bottom && match.right) {
                        return 'nwse-resize';
                    }
                    if (match.top || match.bottom) {
                        return 'ns-resize';
                    }
                    if (match.left || match.right) {
                        return 'ew-resize';
                    }
                    throw "this was supposed to be a match!";
                }());
            } else if (boxUnderCursorPosition(loc, self.boxes())) {
                e.target.style.cursor = 'move';
            } else {
                e.target.style.cursor = 'default';
            }
        }
    });
    $affordanceCanvas.mouseup(function (e) {
        e.target.style.cursor = 'default';
        if (!selection) {
            // mousedown happened outside of canvas
            // so no selection is in progress
            return;
        }
        self.affordanceBoxes.splice(0, self.affordanceBoxes().length);
        selection.end = getCursorPosition(e);
        selection.endPx = getCursorPositionPx(e);
        var box;
        if (selection.isResize) {
            var endVertex = getClosestVertex(selection.endPx);
            var match = selection.resizeMatch;
            box = match.box;
            var newDimensions = getResizedBox(match, endVertex);
            box.i(newDimensions.i);
            box.j(newDimensions.j);
            box.width(newDimensions.width);
            box.height(newDimensions.height);
        } else if (selection.isDrag) {
            box = selection.dragBox;
            self.selectedBox(box);
            var newPosition = getTransposedBox(box, selection);
            box.i(newPosition.i);
            box.j(newPosition.j);
        } else if (selection.startPx.x === selection.endPx.x && selection.startPx.y === selection.endPx.y) {
            self.selectedBox(null);
        } else {
            var boxDimensions = getBoxFromSelection(selection);
            box = {
                i: ko.observable(boxDimensions.i),
                j: ko.observable(boxDimensions.j),
                width: ko.observable(boxDimensions.width),
                height: ko.observable(boxDimensions.height),
                property: ko.observable(),
                display_text: ko.observable(""),
                format: ko.observable()
            };
            self.boxes.push(box);
            self.selectedBox(box);
        }
        selection = null;
    });
    $affordanceCanvas.keydown(function (e) {
        if (e.keyCode === 8) {
            e.preventDefault();
            self.boxes.remove(self.selectedBox());
            self.selectedBox(null);
        }
    });

    /*
    Canvas gets rendered using a ko.computed, and unlikely match
    that actually works perfectly for this situation.
    ko.computed runs the function once when it's declared;
    on that first run, it keeps track of all observables called.
    Any time one of those observables changes, it calls the function again.
    This is exactly what we want--- refresh the canvas any time a variable
    it depends on changes.
     */
    var clearCanvas = function (context) {
        context.clearRect ( 0 , 0 , tileWidth * u, tileHeight * u);
    };
    var drawGrid = function (context) {
        context.strokeStyle = "#f2f2f1";
        for (var i = 0; i < tileWidth; i++) {
            context.moveTo(i * u, 0);
            context.lineTo(i * u, tileHeight * u);
        }
        for (var j = 0; j < tileHeight; j++) {
            context.moveTo(0, j * u);
            context.lineTo(tileWidth * u, j * u);
        }
        context.stroke();
    };
    var drawBox = function (context, box, isSelected) {
        context.strokeStyle = '#002c5f';
        context.globalAlpha = 0.5;
        if (isSelected) {
            context.fillStyle = '#004ebc';
        } else {
            context.fillStyle = '#bcdeff';
        }
        context.fillRect(
            box.i() * u,
            box.j() * u,
            box.width() * u,
            box.height() * u
        );
        context.strokeRect(
            box.i() * u,
            box.j() * u,
            box.width() * u,
            box.height() * u
        );
        context.globalAlpha = 1;
        context.fillStyle = '#002c5f';
        context.font = "bold 12px sans-serif";
        context.textAlign = "center";
        context.textBaseline = "middle";
        // affordance box does not have display_text
        if (box.display_text) {
            context.fillText(
                box.display_text(),
                (box.i() + box.width() / 2) * u,
                (box.j() + box.height() / 2) * u
            );
        }
    };
    ko.computed(function () {
        clearCanvas(context);
        drawGrid(context);
        _(self.boxes()).map(function (box) {
            drawBox(context, box, box === self.selectedBox());
        });
    }).extend({throttle: 100});
    ko.computed(function () {
        affordanceContext.setLineDash([5]);
        clearCanvas(affordanceContext);
        _(self.affordanceBoxes()).map(function (box) {
            drawBox(affordanceContext, box, false);
        });
    }).extend({throttle: 10});
    return self;
}
