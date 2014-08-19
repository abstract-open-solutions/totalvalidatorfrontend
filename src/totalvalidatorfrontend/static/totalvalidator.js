/*global window, jQuery, document*/
(function ($) {
    "use strict";


    $(document).ready(function () {

        $('.showhide-trigger').click(function (evt) {
            var link = $(this),
                showhidepanel = link.siblings('.showhide-panel');
            showhidepanel.toggle();
            link.toggleClass('folded unfolded');
            evt.preventDefault();
        });



        // $('#new_session').click(function (evt) {
        //     var options = {
        //         remote: $(this).attr('href')
        //     };
        //     $('#modal-placeholder').modal(options);
        //     evt.preventDefault();
        // });

    });

}(jQuery));
