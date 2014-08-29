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


        $('#change-language select').change(function () {
            this.form.submit();
        });

    });

}(jQuery));
