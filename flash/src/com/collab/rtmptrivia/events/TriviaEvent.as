// Copyright (c) The rtmp-trivia Project.
// See LICENSE.txt for details.
package com.collab.rtmptrivia.events
{
	import flash.events.Event;
	
	/**
	 * @langversion 3.0
     * @playerversion Flash 9
	 */	
	public class TriviaEvent extends Event
	{
		// ====================================================================
		// CONSTANTS
		// ====================================================================
		
		public static const NEW_HINT				: String = "newHint";
		public static const NEW_QUESTION			: String = "newQuestion";
		public static const SHOW_ANSWER				: String = "showAnswer";
		public static const CORRECT_ANSWER			: String = "correctAnswer";
		public static const CHAT_MESSAGE			: String = "chatMessage";
		public static const UPDATE_HIGHSCORE		: String = "updateHighscore";
		public static const UPDATE_RESPONSE_RECORD	: String = "updateResponseRecord";
		
		public static const CONNECTION_SUCCESS		: String = "connectionSuccess";
		public static const CONNECTION_CLOSED		: String = "connectionClosed";
		public static const CONNECTION_FAILED		: String = "connectionFailed";
		
		// ====================================================================
		// PRIVATE VARS
		// ====================================================================
		
		private var _hintIndex						: Number;
		private var _answer  						: String;
		private var _hint	  						: String;
		private var _question  						: Object;
		private var _username						: String;
		private var _message						: String;
		private var _score							: Number;
		
		// ====================================================================
		// GETTER/SETTER
		// ====================================================================
		
		/**
		 * @return 
		 */		
		public function get score():Number
		{
			return _score;
		}
		public function set score(value:Number):void
		{
			_score = value;
		}

		/**
		 * @return 
		 */		
		public function get message():String
		{
			return _message;
		}
		public function set message(value:String):void
		{
			_message = value;
		}

		/**
		 * @return 
		 */		
		public function get username():String
		{
			return _username;
		}
		public function set username(value:String):void
		{
			_username = value;
		}

		/**
		 * @return 
		 */		
		public function get hint():String
		{
			return _hint;
		}
		public function set hint(value:String):void
		{
			_hint = value;
		}

		/**
		 * @return 
		 */		
		public function get question():Object
		{
			return _question;
		}
		public function set question(value:Object):void
		{
			_question = value;
		}

		/**
		 * @return 
		 */		
		public function get answer():String
		{
			return _answer;
		}
		public function set answer(value:String):void
		{
			_answer = value;
		}

		/**
		 * @return 
		 */		
		public function get hintIndex():Number
		{
			return _hintIndex;
		}
		public function set hintIndex(value:Number):void
		{
			_hintIndex = value;
		}
		
		/**
		 * Creates a new TriviaEvent object.
		 * 
		 * @param type
		 * @param bubbles
		 * @param cancelable
		 */		
		public function TriviaEvent( type:String, bubbles:Boolean=true,
									 cancelable:Boolean=true )
		{
			super( type, bubbles, cancelable );
		}
		
		/**
		 * @private 
		 */		
		override public function toString():String
		{
			var base:String = "<TriviaEvent type='" + type;
			
			switch ( type )
			{
				case NEW_HINT:
					base += " index='" + _hintIndex + "' hint='" + _hint;
					break;
				
				case SHOW_ANSWER:
					base += " answer='" + _answer + "'/>";
					break;
				
				case NEW_QUESTION:
					base += " id='" + _question.id + "' question='" + _question.question;
					break;
				
				case CHAT_MESSAGE:
					base += " username='" + _username + "' message='" + _message;
					break;
				
				case UPDATE_HIGHSCORE:
					base += " score='" + _score + "'/>";
					break;
			}
			
			return base + "'/>";
		}
		
	}
}