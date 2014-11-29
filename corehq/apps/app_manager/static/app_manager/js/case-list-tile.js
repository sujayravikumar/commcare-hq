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
    var getCursorPosition = function (e) {
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
            i: Math.floor(x/u),
            j: Math.floor(y/u)
        };
    };
    var boxUnderCursorPosition = function (loc, boxesArray) {
        /* boxesArray is a dumb array, not ko.ObservableArray */
        var loc = selection.start;

        for (var a = 0; a < boxesArray.length; a++) {
            var box = boxesArray[a];
            if (box.i() <= loc.i && loc.i < box.i() + box.width() &&
                box.j() <= loc.j && loc.j < box.j() + box.height()) {
                return box;
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
        var box = boxUnderCursorPosition(selection.start, self.boxes());
        if (box) {
            selection.isDrag = true;
            selection.dragBox = box;
        } else {
            selection.isDrag = false;
            selection.dragBox = null;
        }
    });
    $affordanceCanvas.mousemove(function (e) {
        if (!selection) {
            // mouse is just moving around in the canvas
            // no selection is happening
            return;
        }
        var affordanceSelection = {
            start: {i: selection.start.i, j: selection.start.j},
            end: getCursorPosition(e)
        };
        if (selection.isDrag) {
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
    });
    $affordanceCanvas.mouseup(function (e) {
        if (!selection) {
            // mousedown happened outside of canvas
            // so no selection is in progress
            return;
        }
        self.affordanceBoxes.splice(0, self.affordanceBoxes().length);
        selection.end = getCursorPosition(e);
        // check if this was a drag
        var box;
        if (selection.isDrag) {
            box = selection.dragBox;
            self.selectedBox(box);
            var newPosition = getTransposedBox(box, selection);
            box.i(newPosition.i);
            box.j(newPosition.j);
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
