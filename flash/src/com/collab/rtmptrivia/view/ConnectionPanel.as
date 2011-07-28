// Copyright (c) The rtmp-trivia Project.
// See LICENSE.txt for details.
package com.collab.rtmptrivia.view
{
	import com.collab.rtmptrivia.events.TriviaEvent;
	import com.collab.rtmptrivia.net.TriviaClient;
	
	import flash.events.Event;
	import flash.events.MouseEvent;
	import flash.events.NetStatusEvent;
	import flash.events.SecurityErrorEvent;
	import flash.net.NetConnection;
	import flash.net.ObjectEncoding;
	
	import mx.events.FlexEvent;
	
	import spark.components.Button;
	import spark.components.HGroup;
	import spark.components.Label;
	import spark.components.Panel;
	import spark.components.RichEditableText;
	import spark.components.TextInput;
	import spark.layouts.HorizontalAlign;
	import spark.layouts.HorizontalLayout;
	import spark.layouts.VerticalAlign;
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
		private const JOIN				: String = "Join";
		private const JOIN_SERVICE		: String = "playTrivia";
		private const ANSWER_SERVICE	: String = "giveAnswer";
		
		private var _status				: RichEditableText;
		private var _connect			: Button;
		private var _join				: Button;
		private var _submit				: Button;
		private var _host				: TextInput;
		private var _input				: TextInput;
		private var _gatewayLabel		: Label;
		
		private var _url				: String = "rtmp://localhost:1935/trivia";
		private var _nc					: NetConnection;
		private var _title				: String;
		private var _username			: String;
		private var _client				: TriviaClient;
		
		/**
		 * Creates a new ConnectionPanel object.
		 * 
		 * @param title		Title for the panel.
		 */		
		public function ConnectionPanel( title:String="Trivia", username:String="User1" )
		{
			super();
			
			_username = username;
			
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
			
			if ( !_gatewayLabel )
			{
				_gatewayLabel = new Label();
				_gatewayLabel.text = "Host:";
			}
			
			if ( !_host )
			{
				_host = new TextInput();
				_host.text = _url;
				_host.width = 200;
			}
			
			if ( !_connect )
			{
				_connect = new Button();
				_connect.label = CONNECT;
				_connect.minWidth = 90;
				_connect.addEventListener( MouseEvent.CLICK, connectClickHandler );
			}
			
			if ( !_join )
			{
				_join = new Button();
				_join.enabled = false;
				_join.label = JOIN;
				_join.addEventListener( MouseEvent.CLICK, joinClickHandler );
			}
			
			if ( !_input )
			{
				var gr:HGroup = new HGroup();
				gr.verticalAlign = VerticalAlign.MIDDLE;
				gr.percentWidth = 100;
				gr.paddingLeft = 40;
				
				_input = new TextInput();
				_input.addEventListener( FlexEvent.ENTER, submitHandler );
				_input.enabled = false;
				_input.percentWidth = 100;
				gr.addElement( _input );
			}
			
			if ( !_submit )
			{
				_submit = new Button();
				_submit.label = "Send";
				_submit.enabled = false;
				_submit.minWidth = 90;
				_submit.addEventListener( MouseEvent.CLICK, submitHandler );
				gr.addElement( _submit );
			}

			if ( !controlBarContent )
			{
				controlBarContent = [ _gatewayLabel, _host, _connect, _join,
					                  gr ];
				var l:HorizontalLayout = new HorizontalLayout();
				l.horizontalAlign = HorizontalAlign.CENTER;
				l.verticalAlign = VerticalAlign.MIDDLE;
				l.paddingBottom = l.paddingTop = l.paddingLeft = l.paddingRight = 15;
				controlBarLayout = l;
			}
		}
		
		private function connect():void
		{
			log( "" );
			log( "Connecting to " + _url + " with username: " + _username );
			
			_nc.connect( _url, _username );
		}
		
		private function disconnect():void
		{
			_connect.label = CONNECT;
			_join.enabled = _submit.enabled = _input.enabled = false;
			_input.text = "";
		}
		
		private function join():void
		{
			var param:Boolean = true;
			
			trace( "\nCalling '" + JOIN_SERVICE + "' with param: " + param );
			
			_submit.enabled = _input.enabled = true;
			_nc.call( JOIN_SERVICE, null, param );
		}
		
		private function giveAnswer( answer:String ):void
		{
			trace( "Calling '" + ANSWER_SERVICE + "' with answer: " + answer );
			
			_nc.call( ANSWER_SERVICE, null, answer, _username, 0 );
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
		
		private function connectClickHandler( event:MouseEvent ):void
		{
			var url:String = _host.text;
			
			if ( url.length > 0 )
			{
				_url = url;
			
				switch ( _connect.label )
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
		
		private function submitHandler( event:Event ):void
		{
			event.stopImmediatePropagation();
			
			var msg:String = _input.text;
			
			if ( msg.length > 0 )
			{
				_input.text = "";
				
				giveAnswer( msg );
			}
		}
		
		private function joinClickHandler( event:MouseEvent ):void
		{
			if ( _nc.connected )
			{
				join();
			}
		}
		
		private function onStatus( event:NetStatusEvent ):void
		{
			log( event.info.code );
			
			switch ( event.info.code )
			{
				case "NetConnection.Connect.Success":
					_connect.label = DISCONNECT;
					_join.enabled = true;
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
