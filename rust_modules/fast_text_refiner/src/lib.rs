use pyo3::prelude::*;
use regex::Regex;

/// Python에서 사용할 함수: refine_text
#[pyfunction]
fn refine_text(text: &str) -> PyResult<String> {
    // 1. 줄바꿈 제거
    let cleaned = text.replace("\n", " ");

    // 2. 중복 공백 제거
    let re_space = Regex::new(r"\s+").unwrap();
    let cleaned = re_space.replace_all(&cleaned, " ");

    // 3. 양 끝 공백 제거
    Ok(cleaned.trim().to_string())
}

/// 모듈 정의
#[pymodule]
fn fast_text_refiner(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(refine_text, m)?)?;
    Ok(())
}