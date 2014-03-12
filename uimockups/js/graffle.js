Raphael.fn.connection = function (obj1, obj2, line, bg) {
    if (obj1.line && obj1.from && obj1.to) {
        line = obj1;
        obj1 = line.from;
        obj2 = line.to;
    }
    var bb1 = obj1.getBBox(),
        bb2 = obj2.getBBox(),
        p = [{x: bb1.x + bb1.width / 2, y: bb1.y - 1},
        {x: bb1.x + bb1.width / 2, y: bb1.y + bb1.height + 1},
        {x: bb1.x - 1, y: bb1.y + bb1.height / 2},
        {x: bb1.x + bb1.width + 1, y: bb1.y + bb1.height / 2},
        {x: bb2.x + bb2.width / 2, y: bb2.y - 1},
        {x: bb2.x + bb2.width / 2, y: bb2.y + bb2.height + 1},
        {x: bb2.x - 1, y: bb2.y + bb2.height / 2},
        {x: bb2.x + bb2.width + 1, y: bb2.y + bb2.height / 2}],
        d = {}, dis = [];
    for (var i = 0; i < 4; i++) {
        for (var j = 4; j < 8; j++) {
            var dx = Math.abs(p[i].x - p[j].x),
                dy = Math.abs(p[i].y - p[j].y);
            if ((i == j - 4) || (((i != 3 && j != 6) || p[i].x < p[j].x) && ((i != 2 && j != 7) || p[i].x > p[j].x) && ((i != 0 && j != 5) || p[i].y > p[j].y) && ((i != 1 && j != 4) || p[i].y < p[j].y))) {
                dis.push(dx + dy);
                d[dis[dis.length - 1]] = [i, j];
            }
        }
    }
    if (dis.length == 0) {
        var res = [0, 4];
    } else {
        res = d[Math.min.apply(Math, dis)];
    }
    var x1 = p[res[0]].x,
        y1 = p[res[0]].y,
        x4 = p[res[1]].x,
        y4 = p[res[1]].y;
    dx = Math.max(Math.abs(x1 - x4) / 2, 10);
    dy = Math.max(Math.abs(y1 - y4) / 2, 10);
    var x2 = [x1, x1, x1 - dx, x1 + dx][res[0]].toFixed(3),
        y2 = [y1 - dy, y1 + dy, y1, y1][res[0]].toFixed(3),
        x3 = [0, 0, 0, 0, x4, x4, x4 - dx, x4 + dx][res[1]].toFixed(3),
        y3 = [0, 0, 0, 0, y1 + dy, y1 - dy, y4, y4][res[1]].toFixed(3);
    var path = ["M", x1.toFixed(3), y1.toFixed(3), "C", x2, y2, x3, y3, x4.toFixed(3), y4.toFixed(3)].join(",");
    if (line && line.line) {
        line.bg && line.bg.attr({path: path});
        line.line.attr({path: path});
    } else {
        var color = typeof line == "string" ? line : "#000";
        return {
            bg: bg && bg.split && this.path(path).attr({stroke: bg.split("|")[0], fill: "none", "stroke-width": bg.split("|")[1] || 3}),
            line: this.path(path).attr({stroke: color, fill: "none"}),
            from: obj1,
            to: obj2
        };
    }
};

window.onload = function () {
    var width = 640;
    var height = 480;
    var radius = 180;

    var r = Raphael("diagram-canvas", width, height),
        shapes = r.set(),
        labels = r.set(),
        connections = [];

    var devices = [
        'loadgen103',
        'power6',
        'loadgen104',
        'loadgen105'
    ];

    // draw circle to illustrate process, to be removed later
    var circle = r.circle(width/2, height/2, radius);
    circle.attr({stroke:'#e0e0e0'});

    // draw labels circular around center label
    var num_on_circle = devices.length - 1;
    for(var i=0; i<devices.length; i++) {
        if (i==0) {
            x = width / 2;
            y = height / 2;    
        } else {
            x = width / 2 + radius * Math.cos( i/num_on_circle * 2*Math.PI - Math.PI/4 );
            y = height / 2 + radius * Math.sin( i/num_on_circle * 2*Math.PI - Math.PI/4);
        }
        labels.push( r.text(x,y,devices[i]) ); 
    }
    labels.attr({font: "12px Arial", fill: "#222"});

    // draw rounded rects around labels
    labels.forEach(function(label){
        var box = label.getBBox(),
            rect_width  = box.width + 40,
            rect_height = 40;
        shapes.push(
            r.rect(label.attr('x') - rect_width/2, label.attr('y')- rect_height/2, rect_width, rect_height, 10)
        );
    });
    shapes.attr({href:'#',fill: '#fff', stroke: '#f90', "fill-opacity": 0, "stroke-width": 2});

    // make connections from center shape to all other shapes
    for(var i=1; i<shapes.length;i++) {
        connections.push(r.connection(shapes[0], shapes[i], "#fff", "#333"));
    }
};