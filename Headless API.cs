using PuppeteerSharp;
using Newtonsoft.Json;
using System.Text.RegularExpressions;
using System.Net.Http;
using System.IO;
using System;
using System.Threading.Tasks;

namespace PACIProcessingLibrary
{
    public class PACIProcessor
    {
        public static void CaptureData(
            string paciNumber,
            string baseUrl,
            string browserPath,
            int waitTimeMs,
            string urlPatternRegex,
            string outputFolderPath,
            out string resultMessage,
            out string errorMessage)
        {
            resultMessage = "";
            errorMessage = "";

            try
            {
                // Log the initial call
                File.AppendAllText(@"C:\Temp\paci_debug_log.txt", 
                    $"DLL called at {DateTime.Now}\n" +
                    $"paciNumber: {paciNumber}\nbaseUrl: {baseUrl}\n" +
                    $"browserPath: {browserPath}\nwaitTimeMs: {waitTimeMs}\n" +
                    $"urlPatternRegex: {urlPatternRegex}\noutputFolderPath: {outputFolderPath}\n");

                // Run async task synchronously
                Task.Run(() => CaptureSearchRequestAndSaveResponse(
                    paciNumber, baseUrl, browserPath, waitTimeMs, urlPatternRegex, outputFolderPath)).Wait();

                resultMessage = $"Success: JSON saved for PACI {paciNumber}";
                File.AppendAllText(@"C:\Temp\paci_debug_log.txt", $"DLL Ended at {DateTime.Now}\n");
            }
            catch (Exception ex)
            {
                resultMessage = "Error";
                errorMessage = ex.ToString();
                File.AppendAllText(@"C:\Temp\paci_debug_log.txt", $"Exception: {ex}\n");
            }
        }

        private static async Task CaptureSearchRequestAndSaveResponse(
            string paci,
            string baseUrl,
            string browserPath,
            int waitTimeMs,
            string urlPatternRegex,
            string outputFolderPath)
        {
            var launchOptions = new LaunchOptions
            {
                ExecutablePath = browserPath,
                Headless = true
            };

            var browser = await Puppeteer.LaunchAsync(launchOptions);
            var page = await browser.NewPageAsync();

            page.Request += async (sender, e) =>
            {
                string requestUrl = e.Request.Url;

                if (Regex.IsMatch(requestUrl, urlPatternRegex, RegexOptions.IgnoreCase))
                {
                    await FetchAndSaveApiResponse(paci, requestUrl, outputFolderPath);
                }
            };

            try
            {
                await page.GoToAsync(baseUrl + paci);
                await Task.Delay(waitTimeMs); // Wait for page to fully load
            }
            finally
            {
                await browser.CloseAsync();
            }
        }

        private static async Task FetchAndSaveApiResponse(string paci, string requestUri, string outputFolderPath)
        {
            using (var client = new HttpClient())
            {
                try
                {
                    var response = await client.GetAsync(requestUri);
                    response.EnsureSuccessStatusCode();

                    string rawJson = await response.Content.ReadAsStringAsync();
                    var formattedJson = JsonConvert.SerializeObject(JsonConvert.DeserializeObject(rawJson), Formatting.Indented);

                    string safeFileName = SanitizeFileName(paci) + ".json";
                    string filePath = Path.Combine(outputFolderPath, safeFileName);

                    File.WriteAllText(filePath, formattedJson);
                }
                catch (HttpRequestException hre)
                {
                    throw new Exception("HTTP Request Failed: " + hre.Message);
                }
                catch (Exception ex)
                {
                    throw new Exception("FetchAndSaveApiResponse error: " + ex.Message);
                }
            }
        }

        private static string SanitizeFileName(string input)
        {
            return Regex.Replace(input, "[^a-zA-Z0-9]", "_").ToLowerInvariant();
        }
    }
}





ErrorMsg="";
try{    
// Call the static method from the external DLL
    PACIProcessor.CaptureData(
        paciNumber,        // Input Data Item
        baseUrl,           // Input Data Item
        browserPath,       // Input Data Item
        (int)waitTimeMs,   // Input Data Item (Number)
        urlPatternRegex,
		outputFolderPath);  // Input Data Item
		ErrorMsg ="False";
}catch (Exception ex)
{
    ErrorMsg = "Exception: " + ex.Message;
}