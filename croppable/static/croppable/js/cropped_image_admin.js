(function ($) {
    "use strict";

    $(document).ready(function() {
        // go through all jcrop file inputs on the page
        $.each($('.jcrop_file'), function(i, v) {
            var fileInput = $(v);
            var existingImgUrl = fileInput.attr('data-existing-img-url');
            var targetImgId = fileInput.attr('data-target-img-id');

            // if there is a URL, load that image and set up Jcrop based on data stored in jcrop file input elemenet
            if(existingImgUrl){
                var imgToCrop = document.createElement('img');

                $(imgToCrop).attr('src', existingImgUrl).attr('id', targetImgId).hide();

                // only initialize Jcrop after the image has loaded
                $(imgToCrop).load(function() {
                    $(imgToCrop).show().Jcrop(
                        getJcropOptions(fileInput, false)
                    );
                });

                // insert the image after the file input
                fileInput.after(imgToCrop);
            }

        });

        // runs whenever a new file is selected in a jcrop file input
        $('.jcrop_file').change(function(){
            loadLocalImage($(this));
        });

        // given a CSV crop coordinate string (w,h,x,y), return box coordinates for setting Jcrop (x1,y1,x2,y2)
        function getBoxCoords(csvCropCoords){
            var cropCoords = csvCropCoords.split(',');
            var x1, y1, x2, y2;
            var boxCoords = null;

            if(cropCoords.length == 4) {
                x1 = parseInt(cropCoords[2]);
                y1 = parseInt(cropCoords[3]);
                x2 = x1 + parseInt(cropCoords[0]);
                y2 = y1 + parseInt(cropCoords[1]);
                boxCoords = [x1, y1, x2, y2];
            }

            return boxCoords;
        }

        // Jcrop's onSelect event only passes a single coordinates argument
        // this returns a handler function that we use to pass other arguments
        function createCoordHandler(coordsFieldId, imgId) {
            return function(c) {
                setCropCoords(c, coordsFieldId, imgId);
            }
        }

        function createReleaseHandler(coordsFieldId, imgId) {
            return function() {
                setCropCoords(null, coordsFieldId, imgId);
            }
        }

        // updates the value of the coordinate field to contain the appropraite CSV
        function setCropCoords(c, coordsFieldId, imgId) {
            if(c) {
                $('#' + coordsFieldId).val(c.w + ',' + c.h + ',' + c.x + ',' + c.y);
            } else {
                $('#' + coordsFieldId).val(',');
            }
        }

        // create jcrop options dictionary from jcrop file input data dictionary
        function getJcropOptions(d, isNewImage) {
            var options = {
                onSelect: createCoordHandler(d.attr('data-coords-field-id'), d.attr('data-target-img-id')),
                onRelease: createReleaseHandler(d.attr('data-coords-field-id'), d.attr('data-target-img-id')),
                allowSelect: ! d.attr('data-fix-aspect-ratio'),
                aspectRatio: d.attr('data-fix-aspect-ratio') * (d.attr('data-initial-crop-width') / d.attr('data-initial-crop-height'))
            }

            var initial_crop;
            if(!isNewImage) {
                var coordsCSV = $('#' + d.attr('data-coords-field-id')).val();
                initial_crop = getBoxCoords(coordsCSV);
            } else {
                initial_crop = [0, 0, d.attr('data-initial-crop-width'), d.attr('data-initial-crop-height')];
            }

            if(initial_crop) {
                options['setSelect'] = initial_crop;
            }

            if(d.attr('data-min-image-width') && d.attr('data-min-image-height')){
                options['minSize'] = [d.attr('data-min-image-width'), d.attr('data-min-image-height')];
            }

            options['onRelease'] = function(){
                if(!options['allowSelect']){
                    this.setSelect(this.tellSelect());
                    this.enable();
                }
            };
            
            return options
        }

        // given a file input element rendered by the JCropWidget Django widget, display the local image it points to and set up Jcrop
        function loadLocalImage(fileInput) {
            var file = fileInput[0].files[0];
            var targetImgId = fileInput.attr('data-target-img-id');
            var coordsFieldId = fileInput.attr('data-coords-field-id');

            // clear coordinates field
            $('#' + coordsFieldId).val('');

            // clean up previously existing jcrop elements for this jcrop file input
            var existingImg = fileInput.next('[id=' + targetImgId + ']');
            existingImg.next('.jcrop-holder').remove();
            existingImg.remove();

            // create a new img element and add to DOM after the file input
            var imgToCrop = document.createElement('img');
            imgToCrop.file = file;
            fileInput.after(imgToCrop);

            // hide image so that it doesn't appear for a split second if it's too small
            $(imgToCrop).hide();

            // HTML5 file reader to display local image file
            var reader = new FileReader();
            reader.onload = (function(img) {
                                return function(e) {
                                    img.src = e.target.result;
                                    $(img).attr('id', targetImgId);
                                    $(img).Jcrop(
                                        getJcropOptions(fileInput, true), function() {
                                            // destroy Jcrop and remove image if it doesn't meet minimum dimensions
                                            var min_width = fileInput.attr('data-min-image-width');
                                            var min_height = fileInput.attr('data-min-image-height');

                                            if((min_width && img.width < min_width) ||
                                                (min_height && img.height < min_height)){

                                                $(img).remove();
                                                this.destroy();

                                                var msg = 'That image is too small. ';
                                                if(min_width){
                                                    msg += 'The minimum width is ' + min_width + '. ';
                                                }
                                                if(min_height){
                                                    msg += 'The minimum height is ' + min_height + '.';
                                                }

                                                alert(msg);
                                            } else {
                                                // after jcrop initializes, update coords element with initial crop coords
                                                var jcrop_api = this;
                                                setCropCoords(jcrop_api.tellSelect(), coordsFieldId, targetImgId);
                                            }
                                        }
                                    );
                                };
                            })(imgToCrop);
            reader.readAsDataURL(file);
        }

    });

}(jQuery || django.jQuery));
