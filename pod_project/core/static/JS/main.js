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