// Copyright (c) The rtmp-trivia Project.
// See LICENSE.txt for details.
package com.collab.rtmptrivia.view
{
	import com.collab.rtmptrivia.events.TriviaEvent;
	import com.collab.rtmptrivia.net.TriviaClient;
	
	import flash.events.MouseEvent;
	import flash.events.NetStatusEvent;
	import flash.events.SecurityErrorEvent;
	import flash.net.NetConnection;
	import flash.net.ObjectEncoding;
	
	import spark.components.Button;
	import spark.components.Panel;
	import spark.components.RichEditableText;
	import spark.components.TextInput;
	import spark.layouts.VerticalLayout;
	
	/**
	 * Simple fullsize text area (without scroll bars), with ability to
	 * specify custom gateway url, connect/disconnect and make calls.
	 * 
	 * @langversion 3.0
     * @playerversion Flash 10
	 */	
	public class ConnectionPanel extends Panel
	{
		private const CONNECT			: String = "Connect";
		private const DISCONNECT		: String = "Disconnect";
		private const SERVICE_NAME		: String = "playTrivia";
		
		private var _status				: RichEditableText;
		private var _submit				: Button;
		private var _call				: Button;
		private var _gateway			: TextInput;
		
		private var _url				: String = "rtmp://localhost:1935/trivia";
		private var _nc					: NetConnection;
		private var _title				: String;
		private var _client				: TriviaClient;
		
		/**
		 * Creates a new ConnectionPanel object.
		 * 
		 * @param title		Title for the panel.
		 */		
		public function ConnectionPanel( title:String="Trivia" )
		{
			super();
			
			this.title = title;
			this.layout = new VerticalLayout();
			this.controlBarVisible = true;
		}
		
		/**
		 * @private 
		 */		
		override public function stylesInitialized():void
		{
			super.stylesInitialized();
			
			setStyle( "cornerRadius", 10 );
		}
		
		/**
		 * @private 
		 */		
		override protected function createChildren():void
		{
			super.createChildren();
			
			// client
			if ( !_client )
			{
				_client = new TriviaClient();
				_client.addEventListener( TriviaEvent.NEW_HINT, callbackHandler );
				_client.addEventListener( TriviaEvent.NEW_QUESTION, callbackHandler );
				_client.addEventListener( TriviaEvent.SHOW_ANSWER, callbackHandler );
				_client.addEventListener( TriviaEvent.CORRECT_ANSWER, callbackHandler );
				_client.addEventListener( TriviaEvent.CHAT_MESSAGE, callbackHandler );
				_client.addEventListener( TriviaEvent.UPDATE_RESPONSE_RECORD, callbackHandler );
				_client.addEventListener( TriviaEvent.UPDATE_HIGHSCORE, callbackHandler );
			}
			
			// netconnection
			if ( !_nc )
			{
				_nc = new NetConnection();
				// XXX: switch to AMF3 when rtmpy ticket #132 is resolved
				_nc.objectEncoding = ObjectEncoding.AMF0;
				_nc.client = _client;
				_nc.addEventListener( NetStatusEvent.NET_STATUS, onStatus );
				_nc.addEventListener( SecurityErrorEvent.SECURITY_ERROR, onError );
			}
			
			// status field
			if ( !_status )
			{
				_status = new RichEditableText();
				_status.setStyle( "fontSize", 15 );
				_status.setStyle( "paddingLeft", 5 );
				_status.editable = false;
				_status.percentWidth = 100;
				_status.percentHeight = 100;
				addElement( _status );
			}
			
			if ( !_gateway )
			{
				_gateway = new TextInput();
				_gateway.text = _url;
				_gateway.percentWidth = 100;
			}
			
			if ( !_submit )
			{
				_submit = new Button();
				_submit.label = CONNECT;
				_submit.minWidth = 90;
				_submit.addEventListener( MouseEvent.CLICK, onSubmit );
			}
			
			if ( !_call )
			{
				_call = new Button();
				_call.enabled = false;
				_call.label = "Call";
				_call.addEventListener( MouseEvent.CLICK, onCall );
			}

			if ( !controlBarContent )
			{
				controlBarContent = [ _gateway, _submit, _call ];
			}
		}
		
		private function connect():void
		{
			log( "" );
			log( "Connecting to " + _url );
			
			_nc.connect( _url );
		}
		
		private function disconnect():void
		{
			_submit.label = CONNECT;
			_call.enabled = false;
		}
		
		private function call():void
		{
			var param:Boolean = true;
			
			log( "\nCalling '" + SERVICE_NAME + "' with param: " + param );
			
			_nc.call( SERVICE_NAME, null, param );
		}
		
		private function log( msg:* ):void
		{
			_status.appendText( msg + "\n" );
			
			trace( msg );
		}
		
		private function onResult( result:Object ):void
		{
			log( "call.onResult: " + result );	
		}
		
		private function onFault( fault:Object ):void
		{
			log( "call.onFault: " + fault );	
		}
		
		private function onSubmit( event:MouseEvent ):void
		{
			var url:String = _gateway.text;
			
			if ( url.length > 0 )
			{
				_url = url;
			
				switch ( _submit.label )
				{
					case CONNECT:
						connect();
						break;
					
					case DISCONNECT:
						log( "\nDisconnecting..." );
						_nc.close();
						disconnect();
						break;
				}
			}
		}
		
		private function onCall( event:MouseEvent ):void
		{
			if ( _nc.connected )
			{
				call();
			}
		}
		
		private function onStatus( event:NetStatusEvent ):void
		{
			log( event.info.code );
			
			switch ( event.info.code )
			{
				case "NetConnection.Connect.Success":
					_submit.label = DISCONNECT;
					_call.enabled = true;
					break;
				
				case "NetConnection.Connect.Closed":
					disconnect();
					break;
				
				case "NetConnection.Connect.Failed":
					log( "Could not connect to " + _url );
					break;
			}
		}
		
		private function onError( event:SecurityErrorEvent ):void
		{
			log( event );	
		}
		
		private function callbackHandler( event:TriviaEvent ):void
		{
			event.stopImmediatePropagation();
			
			switch ( event.type )
			{
				case TriviaEvent.NEW_HINT:
					log( "Hint " + event.hintIndex.toString() + ": " + event.hint );
					break;
				
				case TriviaEvent.NEW_QUESTION:
					log( "Question: " + event.question.question );
					break;
				
				case TriviaEvent.SHOW_ANSWER:
					log( "Answer: " + event.answer );
					break;
				
				case TriviaEvent.CHAT_MESSAGE:
					log( event.username + ": " + event.message );
					break;
				
				default:
					log( event );
					break;
			}
		}
		
	}
}
