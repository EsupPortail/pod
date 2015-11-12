
$(document).ready(function() {
    // Lancement de la recherche au clic sur le bouton de recherche
    $(document.body).on(
        'click',
        '#searchBar SPAN BUTTON.submit',
        function() {
            if ($('#searchBar').find('INPUT').val() != '') {
                $(this).closest('FORM').submit();
            }
        }
    );
});



( function( POD, $, undefined ) { 'use strict';


    /*
        Video creation / edition:

            - selecting “Draft” hides “Restricted access” and “Password”

    */
    POD.setVideoEditForm = function( ) {

        // Objects involved
        var $isDraftCheckbox = $( '#id_is_draft' );
        var $isRestrictedCheckboxGroup = $( '#id_is_restricted' ).closest( '.form-group' );
        var $passwordTextInputGroup = $( '#id_password' ).parent( '.form-group' );

        // Initial state
        if ( $isDraftCheckbox.is( ':checked' ) ) {
            $isRestrictedCheckboxGroup.hide( );
            $passwordTextInputGroup.hide( );
        }

        // Dynamic update
        $isDraftCheckbox.on( 'change', function( event ) {
            if ( $( this ).is( ':checked' ) ) {
                $passwordTextInputGroup.slideUp( );
                $isRestrictedCheckboxGroup.slideUp( );
            } else {
                $isRestrictedCheckboxGroup.slideDown( );
                $passwordTextInputGroup.slideDown( );
            }
        } );
    };


} ( window.POD = window.POD || { }, jQuery ) );
