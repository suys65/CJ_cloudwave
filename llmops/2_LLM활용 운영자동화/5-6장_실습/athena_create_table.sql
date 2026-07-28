-- [주의] 교안 원본은 OpenCSVSerde를 사용했으나, OpenCSVSerde는 date 컬럼을
-- ISO 문자열('2026-01-01')이 아닌 UNIX epoch 숫자로만 해석한다.
-- 그 결과 date_format(order_date, ...) 같은 날짜 쿼리(월별 매출 추이 등)가
-- "BAD_DATA: NumberFormatException: For input string: 2026-01-01" 로 실패한다.
-- 이 데이터는 필드에 콤마/따옴표가 없으므로, ISO 날짜를 date 타입으로 올바르게
-- 파싱하는 LazySimpleSerDe(ROW FORMAT DELIMITED)로 생성한다.

CREATE DATABASE IF NOT EXISTS nlp_s3_analytics_db;

DROP TABLE IF EXISTS nlp_s3_analytics_db.ecommerce_sales;

CREATE EXTERNAL TABLE nlp_s3_analytics_db.ecommerce_sales (
    order_id string,
    order_date date,
    customer_id string,
    region string,
    category string,
    product_name string,
    channel string,
    quantity int,
    unit_price int,
    discount_amount int,
    payment_method string,
    is_returned boolean
)
ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ','
    LINES TERMINATED BY '\n'
STORED AS TEXTFILE
LOCATION 's3://nlp-s3-analytics-kyt-892880329905/datasets/ecommerce_sales/'
TBLPROPERTIES (
    'skip.header.line.count' = '1'
);
