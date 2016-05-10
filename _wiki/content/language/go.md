---
title: "go"
date: 2016-01-18 20:29
---

[TOC][]()

# Syntax

## Reflect

    // StructToMap converts a struct into map[fieldName]=fieldValue.
    // If field is array or slice then fieldValue is its length(don't care value).
    // Each field of struct must be exported.
    func StructToMap(in interface{}) map[string]string {
        ret := make(map[string]string)
        v := reflect.ValueOf(in)
        typ := v.Type()
        for i := 0; i < v.NumField(); i++ {
            f := v.Field(i)
            var s string
            switch f.Type().Kind() {
            case reflect.Slice, reflect.Array:
                s = fmt.Sprintf("%d", f.Len())
            default:
                s = fmt.Sprintf("%v", f.Interface())
            }
            ret[typ.Field(i).Name] = s
        }
        return ret
    }

## Receive signals and quit program gracefully

	sc := make(chan os.Signal, 1)
	quit := make(chan bool, 1)
	signal.Notify(sc,
		syscall.SIGHUP,
		syscall.SIGINT,
		syscall.SIGTERM,
		syscall.SIGQUIT)

	go func() {
		sig := <-sc
		fmt.Printf("Got signal [%d] to exit.\n", sig)
		close(quit)
	}()
	<-quit

