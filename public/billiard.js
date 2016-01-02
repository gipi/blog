function initialize() {
    // https://stackoverflow.com/questions/12805309/javascript-library-d3-call-function
    var drag = d3.behavior.drag()
        .on("drag", move);

    function move() {
        var  x = d3.event.x,
             y = d3.event.y,
             dx = d3.event.dx,
             dy = d3.event.dy;


        console.log(d3.event);
        // calculate the angle approximating the length of dragging to the arc's length
        // and dividing for the distance between the two balls' center
        // FIXME: probably there is some weird issue bc of differente space between screen and SVG
        var coeff = 10;
        var angle = (Math.sqrt(dx*dx + dy*dy)/40.0) * Math.PI;
        var direction = dx > dy ? 1 : -1;
        console.log('angle: ' + angle);

        var vf_ob = null;

        d3.select(this)
            .attr("transform", function () {
                    // we add up the rotation
                    var transform = d3.transform(d3.select(this).attr('transform'));
                    if (transform.rotate > 90) {
                        transform.rotate = 90;
                    } else if (transform.rotate < -90){
                        transform.rotate = -90;
                    } else {
                        transform.rotate += direction * coeff * angle;
                    }
                    console.log('rotate: ' + transform.rotate);
                    //transform.rotate += direction*angle;
                    vf_ob = Math.cos(transform.rotate*Math.PI/180);


                    //return 'rotate(' + transform.rotate + ') translate(' + transform.translate[0] + ',' + transform.translate[1] + ')';
                    return 'rotate(' + transform.rotate + ') translate(0, -40)';
            });
        d3.select('#final_velocity').attr('transform', function() {
            return 'scale(1, ' + vf_ob + ')';
        });
    }

    d3.selectAll('#other-ball-rs').call(drag);
}

