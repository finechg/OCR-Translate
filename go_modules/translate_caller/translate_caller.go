package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io/ioutil"
    "net/http"
    "os"
    "time"
)

// 요청 입력 구조
type TranslateRequest struct {
    Text        string `json:"text"`
    SourceLang  string `json:"source_lang"`
    TargetLang  string `json:"target_lang"`
}

// Google API 요청 구조
type GoogleTranslatePayload struct {
    Contents           []string `json:"contents"`
    SourceLanguageCode string   `json:"sourceLanguageCode"`
    TargetLanguageCode string   `json:"targetLanguageCode"`
    MimeType           string   `json:"mimeType"`
}

// 출력 구조
type TranslateResponse struct {
    TranslatedText string `json:"translated_text"`
}

// Google API 응답 구조
type GoogleResponse struct {
    Translations []struct {
        TranslatedText string `json:"translatedText"`
    } `json:"translations"`
}

func main() {
    var req TranslateRequest
    decoder := json.NewDecoder(os.Stdin)
    err := decoder.Decode(&req)
    if err != nil {
        fmt.Fprintf(os.Stderr, "Invalid input: %v\n", err)
        os.Exit(1)
    }

    translated, err := callGoogleTranslate(req.Text, req.SourceLang, req.TargetLang)
    if err != nil {
        fmt.Fprintf(os.Stderr, "API Error: %v\n", err)
        os.Exit(1)
    }

    res := TranslateResponse{TranslatedText: translated}
    resJSON, _ := json.Marshal(res)
    fmt.Println(string(resJSON))
}

func callGoogleTranslate(text, sourceLang, targetLang string) (string, error) {
    projectID := os.Getenv("GOOGLE_PROJECT_ID")
    if projectID == "" {
        return "", fmt.Errorf("GOOGLE_PROJECT_ID not set")
    }

    url := fmt.Sprintf("https://translation.googleapis.com/v3/projects/%s/locations/global:translateText", projectID)

    payload := GoogleTranslatePayload{
        Contents:           []string{text},
        SourceLanguageCode: sourceLang,
        TargetLanguageCode: targetLang,
        MimeType:           "text/plain",
    }

    body, _ := json.Marshal(payload)
    req, _ := http.NewRequest("POST", url, bytes.NewBuffer(body))
    req.Header.Set("Content-Type", "application/json")
    client := &http.Client{Timeout: 10 * time.Second}
    resp, err := client.Do(req)
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()

    respBody, _ := ioutil.ReadAll(resp.Body)
    if resp.StatusCode != 200 {
        return "", fmt.Errorf("Google API error: %s", respBody)
    }

    var parsed GoogleResponse
    if err := json.Unmarshal(respBody, &parsed); err != nil {
        return "", err
    }

    return parsed.Translations[0].TranslatedText, nil
}