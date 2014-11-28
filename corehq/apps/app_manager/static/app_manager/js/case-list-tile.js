function CaseListTile(options) {
    var o = {
        unit: options.unit || 40
    };
    var u = o.unit;
    var self = {};
    var $canvas = self.$canvas = $('<canvas width="' + 12 * u + '" height="' + 4 * u + '" tabindex="-1"></canvas>')
        .css({
            border: '1px solid #EEEEEE'
        });
    var context = $canvas.get(0).getContext("2d");
    function renderCanvas(context) {
        context.strokeStyle = "#eee";
        context.fillStyle = '#fff';
        context.fillRect(0, 0, 12 * u, 4 * u);
        for (var i = 0; i < 12; i++) {
            context.moveTo(i * u, 0);
            context.lineTo(i * u, 4 * u);
        }
        for (var j = 0; j < 4; j++) {
            context.moveTo(0, j * u);
            context.lineTo(12 * u, j * u);
        }
        context.stroke();
        context.strokeStyle = '#999';
        _(boxes()).map(function (box) {
            if (box === self.selectedBox()) {
                context.fillStyle = '#f0f0ff';
                context.fillRect(
                    box.i * u,
                    box.j * u,
                    box.width * u,
                    box.height * u
                )
            }
            context.strokeRect(
                box.i * u,
                box.j * u,
                box.width * u,
                box.height * u
            );
            context.fillStyle = '#000';
            context.font = "bold 12px sans-serif";
            context.textAlign = "center";
            context.textBaseline = "middle";
            context.fillText(
                box.display_text(),
                (box.i + box.width / 2) * u,
                (box.j + box.height / 2) * u
            );
        });
    }
    function getCursorPosition(e) {
        var x;
        var y;
        if (e.pageX != undefined && e.pageY != undefined) {
            x = e.pageX;
            y = e.pageY;
        }
        else {
            x = e.clientX + document.body.scrollLeft +
                    document.documentElement.scrollLeft;
            y = e.clientY + document.body.scrollTop +
                    document.documentElement.scrollTop;
        }
        x -= $canvas.get(0).offsetLeft;
        y -= $canvas.get(0).offsetTop;
        return {
            i: Math.floor(x/u),
            j: Math.floor(y/u)
        };
    }
    var selection = {};
    var boxes = ko.observableArray();
    self.selectedBox = ko.observable(null);

    renderCanvas(context);

    var fullState = ko.computed(function () {
        boxes();
        self.selectedBox();
        _(boxes()).map(function (box) {
            box.display_text();
        });
    });
    fullState.subscribe(function () {
        renderCanvas(context);
    });
    $canvas.mousedown(function (e) {
        selection.start = getCursorPosition(e);
    });
    $canvas.mouseup(function (e) {
        selection.end = getCursorPosition(e);
        if (selection.start.i === selection.end.i && selection.start.j === selection.end.j) {
            // this is a click
            var loc = selection.start;
            for (var a = 0; a < boxes().length; a++) {
                var box = boxes()[a];
                if (box.i <= loc.i && loc.i < box.i + box.width &&
                    box.j <= loc.j && loc.j < box.j + box.height) {
                    self.selectedBox(box);
                }
            }
            return;
        }
        if (selection.start.i > selection.end.i) {
            var temp = selection.start.i;
            selection.start.i = selection.end.i;
            selection.end.i = temp;
        }
        if (selection.start.j > selection.end.j) {
            var temp = selection.start.j;
            selection.start.j = selection.end.j;
            selection.end.j = temp;
        }
        var box = {
            i: selection.start.i,
            j: selection.start.j,
            width: (selection.end.i - selection.start.i + 1),
            height: (selection.end.j - selection.start.j + 1),
            property: ko.observable(),
            display_text: ko.observable(""),
            format: ko.observable(),
        };
        boxes.push(box);
        self.selectedBox(box);
    });
    $canvas.keydown(function (e) {
        if (e.target === $canvas.get(0)) {
            if (e.keyCode === 8) {
                e.preventDefault();
                boxes.remove(self.selectedBox());
                self.selectedBox(null);
            }
        }
    });
    return self;
}
