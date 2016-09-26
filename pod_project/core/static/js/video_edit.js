/**
 *  Pod form uploader (XMLHttpRequest Level 2)
 *
 *      Philippe Pomédio - 04/2016
 *
 */



var Pod = ( function ( Pod ) {

    "use strict";

    // Stores localized alert messages
    var _uploadMessages = { };


    /**
     *  Sets alert messages localization.
     *
     */
    Pod.setAjaxUploadMessages = function( uploadMessages ) {

        _uploadMessages = uploadMessages;

    }


    /**
     *  Checks for necessary APIs (File, FormData) and AJAX upload progress support.
     *
     */
    Pod.supportsAjaxUpload = function( ) {

        if ( typeof window.File !== 'undefined'
                && typeof window.FormData !== 'undefined' ) {

            return ( 'onprogress' in new XMLHttpRequest( ) );

        } else {

            return false;
        }

    }


    /**
     *  Sends form content via XHR,
     *      and displays upload progression with BS progress-bar.
     *
     */
    Pod.ajaxUpload = function ( formID, progressBarID, successCallback, failureCallback ) {


        function uploadStarted( uploadEvent ) {

            progressBar.classList.remove( 'hidden' );
        }


        function uploadProgress( uploadEvent ) {

            if ( uploadEvent.lengthComputable ) {

                var percentComplete = Math.round( uploadEvent.loaded * 100 / uploadEvent.total );

                if ( percentComplete > 100 ) {
                    percentComplete = 100;
                }

                progressBarDiv.setAttribute( 'style', "width: " + percentComplete + "%" );
                progressBarSpan.textContent = '\u00a0' + percentComplete + '%\u00a0';

            } else {

                progressBar.innerHTML = _uploadMessages.UPLOAD_PROGRESS_NOT_COMPUTABLE;
            }
        }


        function uploadComplete( uploadEvent ) {

            if ( uploadEvent.target.status == 200 ) {

                var responseData = JSON.parse( uploadEvent.target.response );

                if ( responseData.success ) {

                    successCallback( responseData.url );

                } else {

                    failureCallback( responseData.message, false, 'danger' );
                }

            } else {

                failureCallback(
                    uploadEvent.target.status + " - " + uploadEvent.target.statusText,
                    false,
                    'danger'
                );
            }
        }


        function uploadCanceled( uploadEvent ) {

            failureCallback(
                _uploadMessages.UPLOAD_CANCELED,
                false,
                'warning'
            );
        }


        function uploadFailed( uploadEvent ) {

            failureCallback(
                _uploadMessages.UPLOAD_FAILED,
                false,
                'danger'
            );
        }


        var form = document.getElementById( formID ),
            progressBar = document.getElementById( progressBarID ),
            progressBarDiv = progressBar.querySelector( ':scope > div.progress-bar' ),
            progressBarSpan = progressBarDiv.querySelector( ':scope > span' );

        var formData = new FormData( form ),
            xhr = new XMLHttpRequest( );

        xhr.upload.addEventListener( 'progress', uploadProgress, false );
        xhr.addEventListener( 'loadstart', uploadStarted, false );
        xhr.addEventListener( 'load', uploadComplete, false );
        xhr.addEventListener( 'abort', uploadCanceled, false );
        xhr.addEventListener( 'error', uploadFailed, false );
        xhr.open( 'POST', form.action, true );
        xhr.setRequestHeader( 'X-Requested-With', "XMLHttpRequest" );
        xhr.send( formData );

    }


    return Pod;

} ( Pod || { } ) );


