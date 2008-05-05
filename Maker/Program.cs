using System;
using System.Collections.Generic;
using System.Text;
using System.IO;
using System.Text.RegularExpressions;

namespace Maker
{
	class Program
	{
		static string pathToScripts = "..\\..\\..\\ScheherazadeS60";

		static void Main(string[] args)
		{
			string outputFileName = "..\\..\\..\\Scheherazade.py";

			using (StreamReader tr = File.OpenText(Path.Combine(pathToScripts, "Scheherazade.py")))
			{
				Regex fileReplacement = new Regex(@"#\{\*Import ([^*]+)\*\}");
				string inputFileContent = tr.ReadToEnd();

				inputFileContent = fileReplacement.Replace(inputFileContent, new MatchEvaluator(getFileContent));

				File.Delete(outputFileName);
				using (StreamWriter sw = File.AppendText(outputFileName))
				{
					sw.Write(inputFileContent);
				}
			}			
		}

		static string getFileContent(Match match)
		{
			using (StreamReader sr = File.OpenText(Path.Combine(pathToScripts, match.Groups[1].Value)))
			{
				return sr.ReadToEnd();
			}
		}
	}
}
