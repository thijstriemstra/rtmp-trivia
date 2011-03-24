// Copyright (c) The rtmp-trivia Project.
// See LICENSE.txt for details.
package com.collab.rtmptrivia
{
	/**
	 * @author Thijs Triemstra
	 */	
	public class TestClient
	{
		public var test	: String = "123";
		
		/**
		 * @param param
		 * @return 
		 */		
		public function some_method( param:String ):TestClient
		{
			trace( "some_method(" + param + ")" );
			
			return new TestClient();
		}
		
	}
}