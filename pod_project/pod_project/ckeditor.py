

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Actu',
        'toolbarCanCollapse': 'true',
        #'uiColor' : '#417690',
        'language': 'fr',
        'toolbar_Actu': [
            {'name': 'basicstyles', 'items': [
                'Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph', 'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv',
                                            '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'tools', 'items': ['Maximize']}
        ],
    },

    'complete': {
        'toolbar': 'Complete',
        'toolbarCanCollapse': 'true',
        #'uiColor' : '#417690',
        'language': 'fr',
        'toolbar_Complete': [
            #{ 'name': 'document', 'items' : [ 'Source','-','Save','NewPage','DocProps','Preview','Print','-','Templates' ] },
            {'name': 'clipboard', 'items': [
                'Source', '-', 'Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            #{ 'name': 'editing', 'items' : [ 'Find','Replace','-','SelectAll','-','SpellChecker', 'Scayt' ] },
            #'/',
            {'name': 'basicstyles', 'items': [
                'Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph', 'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv',
                                            '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},  # ,'-','BidiLtr','BidiRtl'
            '/',
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert', 'items': [
                'Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe']},
            {'name': 'styles', 'items': [
                'Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize']}
        ],
    },

}
