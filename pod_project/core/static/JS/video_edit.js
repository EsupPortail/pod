/**
 *  Pod form uploader (XMLHttpRequest Level 2)
 *
 *      Philippe Pomédio - 04/2016
 *
 */



var Pod = ( function ( Pod ) {

    "use strict";


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
    Pod.ajaxUpload = function ( formID, progressBarID, failureCallback ) {


        function uploadStarted( uploadEvent ) {

            progressBar.classList.remove( 'hidden' );
        }


        function uploadProgress( uploadEvent ) {

            if ( uploadEvent.lengthComputable ) {

                var percentComplete = Math.round( uploadEvent.loaded * 100 / uploadEvent.total );

                if ( percentComplete > 100 ) {
                    percentComplete = 100;
                }

                progressBarDiv.setAttribute( 'style', "width:" + percentComplete + "%" );
                progressBarSpan.textContent = percentComplete + '% Complete';

            } else {

                progressBar.innerHTML = "Unable to compute upload progress.";
            }
        }


        function uploadComplete( uploadEvent ) {

            console.log( "status: " + uploadEvent.target.status );
            console.log( "statusText: " + uploadEvent.target.statusText );
            console.log( "responseType: " + uploadEvent.target.responseType );
            console.log( "responseURL: " + uploadEvent.target.responseURL );
            console.log( "response: " + uploadEvent.target.response );

            if ( uploadEvent.target.status == 200 ) {

                var responseData = JSON.parse( uploadEvent.target.response );

                if ( responseData[ 'success' ] ) {

                    show_messages( responseData[ 'message' ], responseData[ 'url' ], 'info' );

                } else {

                    failureCallback( responseData[ 'message' ], false, 'danger' );
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

            failureCallback( "Upload canceled.", false, 'warning' );
        }


        function uploadFailed( uploadEvent ) {

            failureCallback( "Error while uploading or connection dropped.", false, 'danger' );
        }


        var form = document.getElementById( formID ),
            progressBar = document.getElementById( progressBarID ),
            progressBarDiv = progressBar.querySelector( ':scope > div.progress-bar' ),
            progressBarSpan = progressBarDiv.querySelector( ':scope > span.sr-only' );

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

