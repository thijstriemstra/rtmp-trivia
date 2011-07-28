// Copyright (c) The rtmp-trivia Project.
// See LICENSE.txt for details.
package com.collab.rtmptrivia
{
	[RemoteClass(alias="com.collab.rtmptrivia.Question")]
	/**
	 * Question object.
	 */	
	public class Question
	{
		public var id		: String;
		public var question	: String;
		
		/**
		 * Creates a new Question object.
		 *  
		 * @param id
		 * @param question
		 */		
		public function Question( id:String=null, question:String=null )
		{
			this.id = id;
			this.question = question;
		}
		
	}
}