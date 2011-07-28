// Copyright (c) The rtmp-trivia Project.
// See LICENSE.txt for details.
package com.collab.rtmptrivia.events
{
	import flash.events.Event;
	
	/**
	 * 
	 */	
	public class TriviaEvent extends Event
	{
		public static const NEW_HINT		: String = "newHint";
		public static const SHOW_ANSWER		: String = "showAnswer";
		public static const NEW_QUESTION	: String = "newQuestion";
		
		private var _hintIndex				: Number;
		private var _answer  				: String;
		private var _hint	  				: String;
		private var _question  				: Object;
		
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
									 cancelable:Boolean=false )
		{
			super( type, bubbles, cancelable );
		}
		
		override public function toString():String
		{
			var base:String = "<TriviaEvent type='" + type + "'";
			
			switch ( type )
			{
				case NEW_HINT:
					base += " index='" + _hintIndex + "' hint='" + _hint + "'/>";
					break;
				
				case SHOW_ANSWER:
					base += " answer='" + _answer + "'/>";
					break;
				
				case NEW_QUESTION:
					base += " id='" + _question.id + "' question='" + _question.question + "'/>";
					break;
				
				default:
					base += "/>";
			}
			
			return base;
		}
		
	}
}